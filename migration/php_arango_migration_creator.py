import json
from typing import ClassVar

from deepdiff.helper import FlatDeltaRow


# TODO: realize rollback
class PhpArangoMigrationCreator:
    file_head = """<?php

use Database\\ArangoMigration;
use ArangoDBClient\\Collection as ArangoCollection;
use ArangoDBClient\\Document as ArangoDocument;

// Auto-generated migration file.
return new class extends ArangoMigration
{
    /**
     * Run the migrations.
     */
    public function up(): void
    {
    """

    file_footer = """
    }

    /**
     * Reverse the migrations.
     */
    public function down(): void
    {
    }
};
    """

    actions = ClassVar[list[str]]

    def __init__(self) -> None:
        self.diff_dic: dict[str, list[FlatDeltaRow]] = {}

    def add_diff(self, collection_name: str, diff: list[FlatDeltaRow]) -> None:
        """Add a diff to the list of actions."""
        self.diff_dic[collection_name] = diff

    def create_migration(self) -> str:
        """Create a migration class from a flat diff dictionary."""
        return self.file_head + self.__create_actions() + self.file_footer

    def __create_actions(self) -> str:
        """Create the actions from the flat diff dictionary."""
        actions = ""
        for collection_name, diff in self.diff_dic.items():
            actions += self.__create_action(collection_name, diff)
        return actions

    def __create_action(self, collection_name: str, diffs: list[FlatDeltaRow]) -> str:
        """Create an action from a flat diff dictionary."""
        action = ""
        for diff in diffs:
            match diff["action"]:
                case "dictionary_item_added":
                    action += f"""
                $document = ArangoDocument::createFromArray(json_decode('{json.dumps(diff['value'])}', true));
                $this->documentHandler->insert('{collection_name}', $document, ['overwriteMode' => 'ignore']);
                    """
                case "dictionary_item_removed":
                    action += f"""
                $this->collectionHandler->removeByExample('{collection_name}', json_decode('{json.dumps(diff['value'])}', true), ['limit' => 1]);
                    """
        return action
