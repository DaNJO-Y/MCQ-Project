# blue prints are imported 
# explicitly instead of using *
from .user import user_views
from .index import index_views
from .auth import auth_views
from .questions import questions_views
from .admin import setup_admin
from .exams import exams_views
from .tags import tags_views


views = [user_views, index_views, auth_views,questions_views, exams_views, tags_views] 
# blueprints must be added to this list