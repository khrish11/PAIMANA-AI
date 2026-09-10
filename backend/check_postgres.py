import psycopg2

# Connect to PostgreSQL directly
conn = psycopg2.connect(
    host='localhost',
    port=5435,
    database='paimana_ai',
    user='paimana',
    password='paimanapass'
)
conn.autocommit = True
cursor = conn.cursor()

try:
    # Count projects
    cursor.execute('SELECT COUNT(*) FROM projects')
    project_count = cursor.fetchone()[0]
    print(f'Projects count: {project_count}')
    
    # Count CUF submissions
    cursor.execute('SELECT COUNT(*) FROM cuf_submissions')
    cuf_count = cursor.fetchone()[0]
    print(f'CUF submissions count: {cuf_count}')
    
    # Latest reporting month
    cursor.execute('SELECT MAX(reporting_month) FROM cuf_submissions')
    latest_month = cursor.fetchone()[0]
    print(f'Latest reporting month: {latest_month}')
    
    # Count risk scores
    cursor.execute('SELECT COUNT(*) FROM risk_scores')
    risk_count = cursor.fetchone()[0]
    print(f'Risk scores count: {risk_count}')
    
    # Count audit logs
    cursor.execute('SELECT COUNT(*) FROM audit_log')
    audit_count = cursor.fetchone()[0]
    print(f'Audit logs count: {audit_count}')
    
    # Check for SIH-TEST-2026-001
    cursor.execute("SELECT COUNT(*) FROM projects WHERE project_code = 'SIH-TEST-2026-001'")
    test_exists = cursor.fetchone()[0] > 0
    print(f'SIH-TEST-2026-001 exists: {test_exists}')
    
finally:
    cursor.close()
    conn.close()
