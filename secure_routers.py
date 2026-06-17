import os
import re

def secure_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'get_current_user' not in content:
        content = content.replace('from app.api.dependencies import get_db', 'from app.api.dependencies import get_db, get_current_user')
        content = content.replace('from app.models import ', 'from app.models import User, Story, ')
    
    def replacer(match):
        signature = match.group(1)
        body = match.group(2)
        if 'current_user: User = Depends(get_current_user)' not in signature:
            signature = signature.replace('db: Session = Depends(get_db)', 'db: Session = Depends(get_db), current_user: User = Depends(get_current_user)')
        
        if 'db.query(Story).filter(Story.id == story_id)' in body:
            body = body.replace('db.query(Story).filter(Story.id == story_id)', 'db.query(Story).filter(Story.id == story_id, Story.user_id == current_user.id)')
        elif 'db.query(Relationship).filter(Relationship.id == relationship_id)' in body:
            body = body.replace('db.query(Relationship).filter(Relationship.id == relationship_id)', 'db.query(Relationship).join(Story).filter(Relationship.id == relationship_id, Story.user_id == current_user.id)')
        elif 'db.query(DiscoveryEvent).filter(DiscoveryEvent.id == event_id)' in body:
            body = body.replace('db.query(DiscoveryEvent).filter(DiscoveryEvent.id == event_id)', 'db.query(DiscoveryEvent).join(Story).filter(DiscoveryEvent.id == event_id, Story.user_id == current_user.id)')
        elif 'db.query(DiscoveryAnswer).filter(' in body:
            # Needs manual fix probably, but let\'s handle relationships first
            pass
        return signature + ':' + body

    pattern = re.compile(r'(def [a-zA-Z0-9_]+\([^\)]+db: Session = Depends\(get_db\)[^\)]*\)):(.*?)(?=\n@router|\Z)', re.DOTALL)
    content = pattern.sub(replacer, content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

files = ['app/api/v1/relationships.py', 'app/api/v1/discovery.py', 'app/api/v1/reports.py']
for f in files:
    secure_file(f)
