# Migrango

**Migrango** is a utility for comparing collections in ArangoDB and automatically generating migration files. The program allows you to manage connections, perform collection dumps, and create migrations to synchronize data between collections.
## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/golovin-mv/migrango.git
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
## Usage
The program provides several commands such as `compare`, `connection`, `dump`, and `make-migrations`.

For detailed information about available options and commands, run:
   ```bash
  python main.py --help
   ```