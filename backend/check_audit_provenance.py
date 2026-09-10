import psycopg2

conn = psycopg2.connect(host='localhost', port=5435, database='paimana_ai', user='paimana', password='paimanapass')
cursor = conn.cursor()

print("=== Audit Logs (recent 10) ===")
cursor.execute('SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 10')
for row in cursor.fetchall():
    print(f"Action: {row[3]}, Entity: {row[4]}, User: {row[1]}, Role: {row[2]}, Time: {row[0]}")

print("\n=== Import Batches ===")
cursor.execute('SELECT * FROM import_batches ORDER BY started_at DESC LIMIT 5')
for row in cursor.fetchall():
    print(f"Batch: {row[1]}, Status: {row[7]}, New submissions: {row[5]}, Created by: {row[12]}")

print("\n=== CUF Revisions ===")
cursor.execute('SELECT * FROM cuf_revisions ORDER BY revision_number DESC LIMIT 5')
for row in cursor.fetchall():
    print(f"Field: {row[3]}, Old: {row[4]}, New: {row[5]}, Actor: {row[7]}")

print("\n=== Project Provenance ===")
cursor.execute('SELECT project_id, project_code, data_source, source_file, entered_by, import_method FROM projects LIMIT 5')
for row in cursor.fetchall():
    print(f"Project: {row[1]}, Source: {row[2]}, File: {row[3]}, Entered by: {row[4]}, Method: {row[5]}")

print("\n=== Submission Provenance ===")
cursor.execute('SELECT submission_id, project_id, data_source, source_file, submitted_by, import_method FROM cuf_submissions LIMIT 5')
for row in cursor.fetchall():
    print(f"Submission: {row[0]}, Project: {row[1]}, Source: {row[2]}, File: {row[3]}, Submitted by: {row[4]}, Method: {row[5]}")

cursor.close()
conn.close()
