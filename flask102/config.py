import os


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:root@localhost:3306/MicroBlogData2"
    POSTS_PER_PAGE = 5 #25