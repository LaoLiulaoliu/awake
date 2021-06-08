import math
import joblib
import numpy as np
import pandas as pd
import mxnet as mx
import matplotlib.pyplot as plt

from db.candles import load_candles


class Environment(object):
    def __init__(self):
        candle_data = load_candles('trx', '1H', end='2021-05-07T04:00:00')
        self.data = pd.DataFrame(candle_data.values(),
                                 index=candle_data.keys(),
                                 columns=['open', 'high', 'low', 'close', 'vol', 'volCcy'],
                                 dtype=np.float64)
        self.data['pct_change'] = self.data['close'].pct_change()
        self.data.fillna(0, inplace=True)

        self.barpos = 0

        self.buy_fee_rate = 0.0008
        self.sell_fee_rate = 0.0008
        self.order_money = 1000  # 一次买多钱

        self.init = 10000
        self.fund = self.init
        self.position = 0
        self.market_value = 0

        self.total_profit = 0
        self.day_profit = 0

    def reset(self):
        self.barpos = 0

        self.init = 10000
        self.fund = self.init  # 现金
        self.position = 0  # 仓
        self.market_value = 0  # 总价值

        self.total_profit = 0
        self.day_profit = 0

        observation = self.data.iloc[self.barpos].tolist()
        observation.append(self.market_value)
        observation.append(self.position)
        observation.append(self.fund)
        return observation

    def step(self, action):
        current_price = self.data['close'].iloc[self.barpos]
        self.day_profit = self.position * current_price * self.data['pct_change'].iloc[self.barpos]
        if action == 0:
            if self.fund > self.order_money:
                buy_order = math.floor(self.order_money / current_price / 100) * 100
                self.fund -= buy_order * current_price

                buy_fee = buy_order * self.buy_fee_rate
                self.position += buy_order - buy_fee
                print('buy:success')
            else:
                print('buy:not enough fund')

        elif action == 1:
            if self.position * current_price > self.order_money:
                sell_order = math.ceil(self.order_money / current_price / 100) * 100
                self.position -= sell_order
                sell_fee = sell_order * current_price * self.sell_fee_rate
                self.fund += sell_order * current_price - sell_fee
                print("sell:success")
            else:
                print('sell:not enough stock')

        else:
            print('keep still')

        # 重新计算持仓状况，不考虑除权除息
        self.market_value = self.position * current_price + self.fund
        self.total_profit = self.market_value - self.init
        self.barpos += 1

        observation = self.data.iloc[self.barpos].tolist()
        observation.append(self.market_value)
        observation.append(self.position)
        observation.append(self.fund)

        return (observation,
                self.day_profit,
                True if self.barpos == self.data.shape[0] - 1 else False)


class DeepQNetwork(mx.gluon.nn.Block):
    def __init__(self, input_dims, fc1_dims, fc2_dims, n_actions, learning_rate):
        """
        n_actions: buy, sell, hold
        """
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions
        self.learning_rate = learning_rate

        self.fc1 = mx.gluon.nn.Dense(self.fc1_dims, activation='relu')  # an affine operation: y = Wx + b
        self.fc2 = mx.gluon.nn.Dense(self.fc2_dims, activation='relu')
        self.fc3 = mx.gluon.nn.Dense(self.n_actions)

    def init(self):
        self.initialize(mx.init.Xavier())
        self.optimizer = mx.gluon.Trainer(self.collect_params(), 'adam', {'learning_rate': self.learning_rate})
        self.loss = mx.gluon.loss.L2Loss()

    def forward(self, inputs):
        return self.fc3(self.fc2(self.fc1(inputs)))


class Agent(object):
    """
    gamma的折扣率它必须介于0和1之间。越大，折扣越小。意味着学习，agent 更关心长期奖励。另一方面，gamma越小，折扣越大。意味着 agent 更关心短期奖励。
    epsilon探索率ϵ。即策略是以1−ϵ的概率选择当前最大价值的动作，以ϵ的概率随机选择新动作。
    """
    def __init__(self, gamma, epsilon, lr, input_dims, batch_size, n_actions=3,
                 max_mem_size=1000000, eps_min=0.01, eps_dec=5e-4):
        self.gamma = gamma
        self.epsilon = epsilon
        self.eps_min = eps_min
        self.eps_dec = eps_dec
        self.lr = lr
        self.n_actions = n_actions
        self.mem_size = max_mem_size
        self.batch_size = batch_size
        self.mem_cnt = 0

        self.Q_eval = DeepQNetwork(input_dims, 256, 256, self.n_actions, self.lr)
        self.Q_eval.init()

        self.state_memory = np.zeros((self.mem_size, input_dims), dtype=np.float32)
        self.new_state_memory = np.zeros((self.mem_size, input_dims), dtype=np.float32)

        self.action_memory = np.zeros(self.mem_size, dtype=np.int32)
        self.reward_memory = np.zeros(self.mem_size, dtype=np.float32)
        self.terminal_memory = np.zeros(self.mem_size, dtype=np.bool)

    def save_model(self):
        params = self.Q_eval._collect_params_with_prefix()
        model = {key: val._reduce() for key, val in params.items()}
        joblib.dump(model, 'DNN_Params.m')

    def load_model(self):
        model = joblib.load('DNN_Params.m')
        params = self.Q_eval._collect_params_with_prefix()
        for name in model:
            params[name]._load_init(model[name], mx.cpu(), cast_dtype=False, dtype_source='current')

    def choose_action(self, observation):
        """ 1-epsilon的概率执行最大价值操作, epsilon概率执行随机动作.

        observation, 状态state
        """
        if np.random.random() > self.epsilon:
            state = mx.nd.array([observation])  # (1, 10)
            # 神经网络模型得到action的Q value vector
            actions = self.Q_eval.forward(state)
            action = int(mx.nd.argmax(actions).asscalar())
        else:
            action = np.random.choice(self.n_actions)
            print("random action:", action)
        return action

    def store_transition(self, state, action, reward, state_, done):
        """ 存储状态变化
        """
        index = self.mem_cnt % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = done

        self.mem_cnt += 1
        print("store_transition index:", index)

    def learn(self):
        """ 从记忆中抽取batch进行学习
        """
        # memory counter小于一个batch_size, 等待积累数据
        if self.mem_cnt < self.batch_size:
            print("learn:watching")
            return

        # 得到memory大小，不超过mem_size
        max_mem = min(self.mem_cnt, self.mem_size)

        # 随机生成一个batch的memory index，可重复抽取
        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        batch_index = np.arange(self.batch_size, dtype=np.int32)

        # 从state memory中抽取一个batch
        state_batch = mx.nd.array(self.state_memory[batch])
        new_state_batch = mx.nd.array(self.new_state_memory[batch])
        reward_batch = mx.nd.array(self.reward_memory[batch])
        terminal_batch = self.terminal_memory[batch]  # 存储是否结束的bool型变量

        action_batch = self.action_memory[batch]

        with mx.autograd.record():
            # 第batch_index行，取action_batch列,对state_batch中的每一组输入，输出action对应的Q值, (batchsize行，1列)
            q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
            q_next = self.Q_eval.forward(new_state_batch).asnumpy()  # (64, 10) -> (64, 3)
            q_next[terminal_batch] = 0.0  # 如果是最终状态，则将q值置为0
            q_target = reward_batch + mx.nd.array(self.gamma * np.max(q_next, axis=1))

            loss = self.Q_eval.loss(q_target, q_eval)
        loss.backward()
        self.Q_eval.optimizer.step(self.batch_size)

        self.epsilon = self.epsilon - self.eps_dec \
            if self.epsilon > self.eps_min else self.eps_min


def run_dqn():
    environ = Environment()
    agent = Agent(gamma=0.9, epsilon=0.5, lr=0.003, input_dims=10, batch_size=64, n_actions=3, eps_min=0.03)
    profits, eps_history = [], []
    epochs = 100

    for i in range(epochs):
        profit = 0
        done = False
        # can add env_list if have multiple stocks
        observation = environ.reset()
        while not done:
            # as barpos increasing
            action = agent.choose_action(observation)
            observation_, reward, done = environ.step(action)
            profit = environ.total_profit
            agent.store_transition(observation, action, reward, observation_, done)
            agent.learn()
            observation = observation_

        # 保存一下每局的收益，最后画个图
        profits.append(profit)
        eps_history.append(agent.epsilon)
        avg_profits = np.mean(profits[-100:])

        print('episode', i, 'profits %.2f' % profit,
              'avg profits %.2f' % avg_profits,
              'epsilon %.2f' % agent.epsilon)

    agent.save_model()
    x = [i + 1 for i in range(epochs)]
    plt.plot(x, profits)

def predict():
    agent = Agent(gamma=0.9, epsilon=0.5, lr=0.003, input_dims=10, batch_size=64, n_actions=3, eps_min=0.03)
    agent.load_model()