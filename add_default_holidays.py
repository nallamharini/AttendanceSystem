"""
Script to add default Indian public holidays for 2026
Run this to populate the calendar with common holidays
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'smartsense.settings')
django.setup()

from attendance.models import Holiday
from datetime import date

# Define default holidays for 2026
holidays_2026 = [
    {
        'name': 'Republic Day',
        'date': date(2026, 1, 26),
        'description': 'National holiday celebrating the adoption of the Indian Constitution'
    },
    {
        'name': 'Holi',
        'date': date(2026, 3, 14),
        'description': 'Festival of colors and spring celebration'
    },
    {
        'name': 'Good Friday',
        'date': date(2026, 4, 3),
        'description': 'Christian religious holiday'
    },
    {
        'name': 'Independence Day',
        'date': date(2026, 8, 15),
        'description': 'National holiday celebrating India\'s independence from British rule'
    },
    {
        'name': 'Gandhi Jayanti',
        'date': date(2026, 10, 2),
        'description': 'Birth anniversary of Mahatma Gandhi, Father of the Nation'
    },
    {
        'name': 'Dussehra',
        'date': date(2026, 10, 22),
        'description': 'Hindu festival celebrating the victory of good over evil'
    },
    {
        'name': 'Diwali',
        'date': date(2026, 11, 10),
        'description': 'Festival of lights celebrated across India'
    },
    {
        'name': 'Christmas',
        'date': date(2026, 12, 25),
        'description': 'Christian festival celebrating the birth of Jesus Christ'
    }
]

print('Adding default holidays for 2026...\n')

added_count = 0
skipped_count = 0

for holiday_data in holidays_2026:
    # Check if holiday already exists
    if Holiday.objects.filter(date=holiday_data['date']).exists():
        existing = Holiday.objects.get(date=holiday_data['date'])
        print(f'⏭️  Skipping {holiday_data["name"]} - Already exists as "{existing.name}"')
        skipped_count += 1
        continue
    
    # Create holiday
    holiday = Holiday.objects.create(
        name=holiday_data['name'],
        date=holiday_data['date'],
        description=holiday_data['description']
    )
    print(f'✅ Added {holiday.name} on {holiday.date.strftime("%B %d, %Y")}')
    added_count += 1

print(f'\n📊 Summary:')
print(f'   Added: {added_count}')
print(f'   Skipped: {skipped_count}')
print(f'   Total: {len(holidays_2026)}')
print('\n✅ Default holidays setup complete!')
