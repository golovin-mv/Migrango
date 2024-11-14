import os
import json
from typing import ClassVar

from deepdiff.helper import FlatDeltaRow

from migration.action import Action, ActionType
from jinja2 import Environment, FileSystemLoader


class MigrationCreator:
    actions: ClassVar[list[Action]] = []

    def __init__(self, create_collections: list[dict[str, str]], remove_collections: list[dict[str, str]], template: str) -> None:
        self.template = template
        self.diff_dic: dict[str, list[FlatDeltaRow]] = {}
        for collection in create_collections:
            self.actions.append(Action(ActionType.COLLECTION_CREATE, {"value": collection}, collection["name"]))
        for collection in remove_collections:
            self.actions.append(Action(ActionType.DELETE_COLLECTION, {"value": collection}, collection["name"]))

    def add_diff(self, collection_name: str, diff: list[FlatDeltaRow]) -> None:
        """Add a diff to the list of actions."""
        self.diff_dic[collection_name] = diff

    def create_migration(self) -> str:
        """Create a migration class from a flat diff dictionary."""
        self.__create_actions()

        return self.__render_template()

    def __create_actions(self) -> None:
        """Create the actions from the flat diff dictionary."""
        for collection_name, diff in self.diff_dic.items():
            self.__create_action_from_diff(collection_name, diff)

    def __create_action_from_diff(self, collection_name: str, diffs: list[FlatDeltaRow]):
        """Create an action from a flat diff dictionary."""
        for diff in diffs:
            match diff["action"]:
                case "dictionary_item_added":
                    self.actions.append(MigrationCreator.__create_document_create_action(collection_name, diff))
                case "dictionary_item_removed":
                    self.actions.append(Action(ActionType.DOCUMENT_DELETE, {"value": diff["value"]}, collection_name))
                case "type_changes":
                    self.actions.append(
                        Action(ActionType.DOCUMENT_UPDATE, {"id": diff["path"][0], "value": {diff["path"][1]: diff["value"]}}, collection_name)
                    )
                case "values_changed":
                    for _, value in diff["value"].items():
                        self.actions.append(Action(ActionType.DOCUMENT_CREATE, {"value": value}, collection_name))
                case _:
                    raise Exception(f"Unsupported action: {diff['action']}")

    def __render_template(self) -> str:
        """Render the template with the actions."""
        grouped_actions = {}

        for action in self.actions:
            if action.type.value in grouped_actions:
                grouped_actions[action.type.value].append(action.__dict__())
            else:
                grouped_actions[action.type.value] = [action.__dict__()]

        template_dir, template_file = os.path.split(self.template)
        env = Environment(loader=FileSystemLoader(template_dir))
        template = env.get_template(template_file)

        return template.render(actions=grouped_actions, json=json)

    @staticmethod
    def __create_document_create_action(collection_name: str, diff: FlatDeltaRow) -> Action:
        if isinstance(diff["value"], dict):
            return Action(ActionType.DOCUMENT_CREATE, {"value": diff["value"]}, collection_name)

        return Action(ActionType.DOCUMENT_UPDATE, {"id": diff["path"][0], "value": {diff["path"][1]: diff["value"]}}, collection_name)
