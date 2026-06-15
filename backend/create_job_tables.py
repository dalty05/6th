# create_job_tables.py
from app import app, db
from models import JobCategory, Job, JobApplication

with app.app_context():
    # Create tables
    db.create_all()
    print("✅ Job tables created successfully!")
    
    # Add default categories
    default_categories = [
        ('Sales & Marketing', 'sales-marketing', 'Sales and marketing positions', '📈'),
        ('Operations', 'operations', 'Operations and logistics roles', '🚚'),
        ('Finance', 'finance', 'Accounting and finance positions', '💰'),
        ('Human Resources', 'human-resources', 'HR and administration roles', '👥'),
        ('Information Technology', 'it', 'IT and technical positions', '💻'),
        ('Production', 'production', 'Production and manufacturing roles', '🏭'),
        ('Quality Assurance', 'quality-assurance', 'Quality control and assurance', '✅'),
        ('Management', 'management', 'Management and leadership positions', '👔'),
    ]
    
    for name, slug, description, icon in default_categories:
        existing = JobCategory.query.filter_by(slug=slug).first()
        if not existing:
            category = JobCategory(
                name=name,
                slug=slug,
                description=description,
                icon=icon,
                is_active=True
            )
            db.session.add(category)
            print(f"  Added category: {name}")
    
    db.session.commit()
    print("\n✅ Default categories added!")
    
    # Verify tables
    print(f"\n📊 Summary:")
    print(f"  JobCategories: {JobCategory.query.count()}")
    print(f"  Jobs: {Job.query.count()}")
    print(f"  JobApplications: {JobApplication.query.count()}")