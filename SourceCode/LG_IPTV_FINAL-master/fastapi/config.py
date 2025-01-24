from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# MySQL 연결 정보
USERNAME = "admin"         # MySQL 사용자 이름
PASSWORD = "wlals8899!*"         # MySQL 비밀번호
HOST = "lg-db.c5aywgymgt2p.ap-northeast-2.rds.amazonaws.com"  # RDS 호스트 이름
PORT = "3306"                      # MySQL 포트 (기본값: 3306)
DATABASE_NAME = "LG"    # 데이터베이스 이름

SQLALCHEMY_DATABASE_URL = f"mysql+pymysql://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}"

# SQLAlchemy 설정
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
