from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base, sessionmaker
from transitions import Machine

Base = declarative_base()


# 订单数据库模型
class OrderModel(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    state = Column(String)


# 创建数据库引擎和 session
engine = create_engine('sqlite:///orders.db')
Session = sessionmaker(bind=engine)
Base.metadata.create_all(engine)


# 封装带状态机的订单类
class Order:
    states = ['new', 'paid', 'shipped', 'delivered', 'completed', 'cancelled']

    transitions = [
        {'trigger': 'pay', 'source': 'new', 'dest': 'paid'},
        {'trigger': 'ship', 'source': 'paid', 'dest': 'shipped'},
        {'trigger': 'deliver', 'source': 'shipped', 'dest': 'delivered'},
        {'trigger': 'complete', 'source': 'delivered', 'dest': 'completed'},
        {'trigger': 'cancel', 'source': ['new', 'paid', 'shipped', 'delivered'], 'dest': 'cancelled'}
    ]

    def __init__(self, order_id=None):
        self.session = Session()

        if order_id:
            # 载入已有订单
            self.db_order = self.session.query(OrderModel).filter_by(id=order_id).first()
            self.state = self.db_order.state
        else:
            # 创建新订单
            self.db_order = OrderModel(state='new')
            self.session.add(self.db_order)
            self.session.commit()
            self.state = 'new'

        self.machine = Machine(model=self,
                               states=Order.states,
                               transitions=Order.transitions,
                               initial=self.state,
                               after_state_change=self._sync_to_db)

    def _sync_to_db(self):
        self.db_order.state = self.state
        self.session.commit()
        print(f"[DB] Order {self.db_order.id} updated to state: {self.state}")

    def get_id(self):
        return self.db_order.id

    def close(self):
        self.session.close()
