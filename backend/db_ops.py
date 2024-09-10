# pip install sqlalchemy

from sqlalchemy import create_engine, Column, Integer, Float, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

# 创建数据库连接
DATABASE_URL = 'sqlite:///database/data.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()


# 定义基类
class CommonTable(Base):
    __abstract__ = True
    id = Column(Integer, primary_key=True, autoincrement=True)
    count = Column(Integer, nullable=False)
    temp = Column(Float, nullable=False)
    vol_set = Column(Float, nullable=False)
    vol1 = Column(Float, nullable=False)
    vol2 = Column(Float, nullable=False)
    vol3 = Column(Float, nullable=False)
    vol4 = Column(Float, nullable=False)
    vol5 = Column(Float, nullable=False)
    vol6 = Column(Float, nullable=False)
    vol7 = Column(Float, nullable=False)
    vol8 = Column(Float, nullable=False)
    vol9 = Column(Float, nullable=False)
    vol10 = Column(Float, nullable=False)
    vol11 = Column(Float, nullable=False)
    vol12 = Column(Float, nullable=False)
    vol13 = Column(Float, nullable=False)
    vol14 = Column(Float, nullable=False)
    vol15 = Column(Float, nullable=False)
    vol16 = Column(Float, nullable=False)
    vol17 = Column(Float, nullable=False)
    vol18 = Column(Float, nullable=False)
    vol19 = Column(Float, nullable=False)
    vol20 = Column(Float, nullable=False)
    vol21 = Column(Float, nullable=False)
    vol22 = Column(Float, nullable=False)
    datetime = Column(DateTime, default=datetime.datetime.utcnow)


# 定义数据表
class Main(CommonTable):
    __tablename__ = 'main'
    vol_over = Column(Float, nullable=False)
    result = Column(Boolean, nullable=False)


class Over6mV(CommonTable):
    __tablename__ = 'over6mV'


class Over8mV(CommonTable):
    __tablename__ = 'over8mV'


class Over10mV(CommonTable):
    __tablename__ = 'over10mV'

# 创建表
Base.metadata.create_all(engine)

# 创建会话
Session = sessionmaker(bind=engine)


class DatabaseOperations:
    def __init__(self):
        self.session = Session()
        self.table_mapping = {
            'main': Main,
            'over6mV': Over6mV,
            'over8mV': Over8mV,
            'over10mV': Over10mV
        }

    def calculate_vol_over(self, vol_set, *vols):
        """计算vol_over"""
        return max((vol - vol_set) for vol in vols)

    def add_record(self, count, temp, vol_set, vols):
        """添加记录到main表并判断是否插入到over6mV, over8mV, over10mV表"""
        vol_over = self.calculate_vol_over(vol_set, *vols)
        vol_columns = {
            f'vol{i+1}': vol for i, vol in enumerate(vols)
        }
        result = (vol_over > 0.006)
        new_record = Main(count=count, temp=temp, vol_set=vol_set, vol_over=vol_over, result=result, **vol_columns)
        self.session.add(new_record)

        if vol_over > 0.01:
            over10mv_record = Over10mV(count=count, temp=temp, vol_set=vol_set, **vol_columns)
            self.session.add(over10mv_record)
        elif vol_over > 0.008:
            over8mv_record = Over8mV(count=count, temp=temp, vol_set=vol_set, **vol_columns)
            self.session.add(over8mv_record)
        elif vol_over > 0.006:
            over6mv_record = Over6mV(count=count, temp=temp, vol_set=vol_set, **vol_columns)
            self.session.add(over6mv_record)

        self.session.commit()
        return new_record

    def get_record(self, table, record_id):
        """根据ID获取记录"""
        record_class = self.table_mapping.get(table)
        if record_class:
            return self.session.query(record_class).filter(record_class.id == record_id).first()

    def update_record(self, table, record_id, count=None, vol_set=None, vols=None):
        """更新记录"""
        record_class = self.table_mapping.get(table)
        if record_class:
            record = self.session.query(record_class).filter(record_class.id == record_id).first()
            if record:
                if count is not None:
                    record.count = count
                if vol_set is not None:
                    record.vol_set = vol_set
                if vols is not None:
                    for i, vol in enumerate(vols):
                        setattr(record, f'vol{i+1}', vol)
                self.session.commit()
            return record

    def delete_record(self, table, record_id):
        """删除记录"""
        record_class = self.table_mapping.get(table)
        if record_class:
            record = self.session.query(record_class).filter(record_class.id == record_id).first()
            if record:
                self.session.delete(record)
                self.session.commit()
            return record

    def get_all_records(self, table):
        """获取所有记录"""
        record_class = self.table_mapping.get(table)
        if record_class:
            return self.session.query(record_class).all()

    def print_all_records(self, table_name):
        """打印所有记录"""
        all_records = self.get_all_records(table_name)
        print(f"All records in {table_name}:")
        for record in all_records:
            vol_values = [getattr(record, f'vol{i+1}') for i in range(22)]
            print(f"ID: {record.id}, Count: {record.count},  Temp: {record.temp},Vol Set: {record.vol_set}, "
                  f"Vol Over: {getattr(record, 'vol_over', 'N/A')}, "
                  f"Result: {getattr(record, 'result', 'N/A')}, "
                  f"Datetime: {record.datetime}, Vols: {vol_values}")
            print('-'*15)

if __name__ == "__main__":
    db_ops = DatabaseOperations()

    # 添加记录
    vols = [1.1, 2.2, 11.5] + [4.4] * 19
    record = db_ops.add_record(10, 22.4, 5.5, vols)
    print(f"Added record to main: {record.id}")

    # 获取记录
    retrieved_record = db_ops.get_record('main', record.id)
    print(f"Retrieved record from main: {retrieved_record.count}, {retrieved_record.vol_set}")

    # 更新记录
    updated_record = db_ops.update_record('main', record.id, count=20)
    print(f"Updated record in main: {updated_record.count}, {updated_record.result}")

    # # 删除记录
    # db_ops.delete_record('main', record.id)
    # print(f"Deleted record from main: {record.id}")

    # 获取所有记录
    db_ops.print_all_records('over10mV')
