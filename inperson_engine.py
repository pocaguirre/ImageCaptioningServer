import sqlalchemy
from sqlalchemy import Column, ForeignKey, Integer, String, select, inspect
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import Session
import pandas as pd
import json

IMAGE_SET_CSV = "inperson_image_sets.csv"
Base = declarative_base()


def get_image_sets() -> dict:
    image_set_df = pd.read_csv(IMAGE_SET_CSV)
    image_set_dict = {}
    for i, row in image_set_df.iterrows():
        if row['image set'] in image_set_dict:
            image_set_dict[row['image set']].append(f"/static/images/{row['filename']}")
        else:
            image_set_dict[row['image set']] = [f"/static/images/{row['filename']}"]
    for image_set, images in image_set_dict.items():
        assert len(images) == 6, "CSV not fell formatted"
    return image_set_dict

class User(Base):
    __tablename__ = 'user'
    user_id = Column(String(50), primary_key=True)
    age = Column(String(50))
    education = Column(String(50))
    glasses = Column(String(50))
    colorblind = Column(String(50))

    def __repr__(self):
        return f"<User(id='{self.user_id}')>"

class Assignment(Base):
    __tablename__ = 'assignment'
    assignment_id = Column(Integer, primary_key=True)
    user_id = Column(String(50), ForeignKey('user.user_id'))
    condition = Column(String(50))

    def __repr__(self):
        return f"<Assignment(id='{self.assignment_id}', condition='{self.condition}', worker='{self.user_id}')>"

class Answer(Base):
    __tablename__ = 'answer'
    assignment_id = Column(Integer, ForeignKey('assignment.assignment_id'), primary_key=True)
    im_url =  Column(String(50), primary_key=True)
    description = Column(String(50))
    im_time = Column(Integer)
    im_start_time = Column(Integer)
    im_end_time = Column(Integer)
    def __repr__(self):
        return f"<Answer(assignment='{self.assignment_id}', im_url='{self.im_url}')>"

class InPersonEngine:
    """
    This class creates a SQL database named "inperson.sql".
    It contains the following tables:
    - demographics: contains the demographics of the workers.
    - jobs: contains the jobs that the workers have completed.
    - workers: contains the workers.
    - ratings: contains the ratings of the workers.
    """
    def __init__(self, debug=False):
        self.debug = debug
        self.db_name = "inperson.sql"
        self.image_sets = get_image_sets()
        self.engine = self.create_engine()
        self.create_tables()
        self.table_names = {
            'user': User,
            'assignment': Assignment,
            'answer': Answer
        }

    def create_engine(self):
        """
        Creates a SQL engine.
        """
        engine = sqlalchemy.create_engine(f"sqlite:///{self.db_name}")
        return engine

    def create_tables(self):
        """
        Creates the tables in the database.
        add IF NOT EXISTS later
        """
        if self.debug:
            with Session(self.engine) as con:
                # Drop all tables
                con.execute("DROP TABLE IF EXISTS user")
                con.execute("DROP TABLE IF EXISTS assignment")
                con.execute("DROP TABLE IF EXISTS answer")
        Base.metadata.create_all(self.engine)
        return
    
    def check_worker_id(self, worker_id):
        """
        Checks if a worker_id is in the database.
        """
        if inspect(self.engine).has_table('user'):
            with Session(self.engine) as con:
                stmt = select(User.user_id).where(User.user_id == worker_id)
                result = con.execute(stmt).scalars().all()
            return len(result) > 0
        return False
    
    def check_worker_assignment(self, worker_id, assignment_id):
        """
        Checks if a worker has already completed a task.
        """
        if inspect(self.engine).has_table('assignment'):
            with Session(self.engine) as con:
                stmt = select(Assignment.assignment_id).where(Assignment.assignment_id == assignment_id and Assignment.user_id == worker_id)
                result = con.execute(stmt).scalars().all()
            return len(result) > 0
        return False
    
    def get_images(self, worker_id):
        """
        Returns the images of a worker.
        """
        if self.check_worker_id(worker_id):
            return self.image_sets['A']
        else:
            return self.image_sets['B']
    
    def save_data(self, worker_id, assignment_id, condition, answer, demographics):
        """
        Saves the data of a worker.
        """
        if self.check_worker_assignment(worker_id, assignment_id):
            return False
        else:
            with Session(self.engine) as con:
                things = []
                things.append(Assignment(assignment_id=assignment_id, user_id=worker_id, condition=condition))
                if not self.check_worker_id(worker_id):
                    demographics_obj = json.loads(demographics)
                    things.append(User(user_id=worker_id, 
                                        age=demographics_obj['age-input'], 
                                        education=demographics_obj['education-radio'], 
                                        glasses=demographics_obj['glasses-radio'], 
                                        colorblind=demographics_obj['colorblind-radio']))
                answer_obj = json.loads(answer)
                for answer in answer_obj:
                    things.append(Answer(assignment_id=assignment_id, 
                                        im_url=answer['im_url'], 
                                        description=answer['description'], 
                                        im_time=answer['im_time'],
                                        im_start_time=answer['im_start_time'],
                                        im_end_time=answer['im_end_time']))
                con.add_all(things)
                con.commit()
            return True
        
    def dump_table(self, table):
        """
        Dumps the contents of a table.
        """
        with Session(self.engine) as con:
            stmt = select(self.table_names[table])
            result = con.execute(stmt).scalars().all()
        result = [vars(r) for r in result]
        _ = [r.pop('_sa_instance_state') for r in result]
        return result