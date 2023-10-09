/* Migration v0.3 - timespan and datetime.

Timebook v0.3 has breaking changes to the database schema. This includes:
- Renaming the time tracking table from "timesheet" to "timespan".
- Changing the time representation from float-time to datetime.
- Converting the previous model from end_time/duration to start/end fields.
- Renaming the column used to mark archived records from "is_checked" to "is_archived".
- Adding tracking columns "created_at" and "updated_at".

Instructions:
- This migration must be run manually, after the new table has been created.
- Backup your database, run Timebook v0.3 once with the old database to create the new table, then run this script.
- After running this migration, you can drop the old "timesheet" table and run VACUUM to optimize the database.

TODO:
- Integrate Alembic (or another migration tool) to handle migrations.

Tested with SQLite. Other databases may require adjustments.
*/

INSERT INTO timespan (id, description, start_at, end_at, is_archived, created_at, updated_at)
SELECT
  id,
  description,
  datetime(day, '+' || ((end_time * 60) - (duration * 60)) || ' minutes') AS start_at,
  datetime(day, '+' || (end_time * 60) || ' minutes') AS end_at,
  is_checked AS is_archived,
  datetime(day) AS created_at,
  datetime(day) AS updated_at
FROM timesheet
ON CONFLICT(id) DO NOTHING;
