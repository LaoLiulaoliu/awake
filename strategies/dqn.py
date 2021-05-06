import math
import joblib
import numpy as np
import pandas as pd
# import torch
# import torch.nn.functional as F
import mxnet as mx
import matplotlib.pyplot as plt

from db.candles import load_candles


class Environment(object):
    def __init__(self):
        candle_data = load_candles('trx', '1m', begin='2021-01-01T11:00:00', end='2021-04-28T11:00:00')
        self.data = pd.DataFrame(candle_data.values(),
                                 index=candle_data.keys(),
                                 columns=['open', 'high', 'low', 'close', 'vol', 'volCcy'],
                                 dtype=np.float64)
        self.data['pct_change'] = self.data['close'].pct_change()
        self.data.fillna(0, inplace=True)

        self.barpos = 0

        self.buy_fee_rate = 0.0008
        self.sell_fee_rate = 0.0008
        self.order_size = 1000  # 订单大小

        self.init = 10000
        self.fund = self.init
        self.position = 0
        self.market_value = 0

        self.balance = self.init
        self.total_profit = 0
        self.day_profit = 0

    def reset(self):
        self.barpos = 0

        self.init = 10000
        self.fund = self.init
        self.position = 0
        self.market_value = 0

        self.balance = self.init
        self.total_profit = 0
        self.day_profit = 0

        observation = self.data.iloc[self.barpos].tolist()
        observation.append(self.balance)
        observation.append(self.position)
        observation.append(self.fund)
        return observation

    def step(self, action):
        current_price = self.data['close'].iloc[self.barpos]
        self.day_profit = self.position * current_price * self.data['pct_change'].iloc[self.barpos]
        if action == 0:
            if self.fund > self.order_size:
                buy_order = math.floor(self.order_size / current_price / 100) * 100
                self.fund -= buy_order * current_price

                buy_fee = buy_order * self.buy_fee_rate
                self.position += buy_order - buy_fee
                print('buy:success')
            else:
                print('buy:not enough fund')

        elif action == 1:
            if self.position * current_price > self.order_size:
                sell_order = math.ceil(self.order_size / current_price / 100) * 100
                self.position -= sell_order
                sell_fee = sell_order * current_price * self.sell_fee_rate
                self.fund += sell_order * current_price - sell_fee
                print("sell:success")
            else:
                print('sell:not enough stock')

        else:
            print('keep still')

        # 重新计算持仓状况，不考虑除权除息
        self.market_value = self.position * current_price
        self.balance = self.market_value + self.fund
        self.total_profit = self.balance - self.init
        self.barpos += 1

        observation = self.data.iloc[self.barpos].tolist()
        observation.append(self.balance)
        observation.append(self.position)
        observation.append(self.fund)

        return (observation,
                self.day_profit,
                True if self.barpos == self.data.shape[0] - 1 else False)


# class DeepQNet(torch.nn.Module):
#     def __init__(self, input_dims, fc1_dims, fc2_dims, n_actions, lr):
#         super(DeepQNet, self).__init__()
#         self.lr = lr
#         self.input_dims = input_dims
#         self.fc1_dims = fc1_dims
#         self.fc2_dims = fc2_dims
#         self.n_actions = n_actions

#         self.fc1 = torch.nn.Linear(self.input_dims, self.fc1_dims)  # an affine operation: y = Wx + b
#         self.fc2 = torch.nn.Linear(self.fc1_dims, self.fc2_dims)
#         self.fc3 = torch.nn.Linear(self.fc2_dims, self.n_actions)
#         self.optimizer = torch.optim.Adam(self.parameters(), lr=lr)
#         self.loss = torch.nn.MSELoss()

#         self.device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
#         self.to(self.device)

#     def forward(self, state):
#         state.to(self.device)
#         x = F.relu(self.fc1(state.to(torch.float32)))
#         x = F.relu(self.fc2(x))
#         actions = self.fc3(x)

#         return actions


class DeepQNetwork(mx.gluon.nn.Block):
    def __init__(self, input_dims, fc1_dims, fc2_dims, n_actions, learning_rate):
        super(DeepQNetwork, self).__init__()
        self.input_dims = input_dims
        self.fc1_dims = fc1_dims
        self.fc2_dims = fc2_dims
        self.n_actions = n_actions

        self.fc1 = mx.gluon.nn.Dense(self.fc1_dims, activation='relu')  # an affine operation: y = Wx + b
        self.fc2 = mx.gluon.nn.Dense(self.fc2_dims, activation='relu')
        self.fc3 = mx.gluon.nn.Dense(self.n_actions)

        self.optimizer = mx.gluon.Trainer(self.collect_params(), 'adam', {'learning_rate': learning_rate})
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
        self.mem_cntr = 0

        self.Q_eval = DeepQNet(input_dims, 256, 256, self.n_actions, self.lr)

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

    # 存储记忆
    def store_transition(self, state, action, reward, state_, done):
        index = self.mem_cntr % self.mem_size
        self.state_memory[index] = state
        self.new_state_memory[index] = state_
        self.reward_memory[index] = reward
        self.action_memory[index] = action
        self.terminal_memory[index] = done

        self.mem_cntr += 1
        print("store_transition index:", index)

    # observation就是状态state
    def choose_action(self, observation):
        if np.random.random() > self.epsilon:
            # 随机0-1，即1-epsilon的概率执行以下操作,最大价值操作
            state = torch.tensor(observation)
            # 放到神经网络模型里面得到action的Q值vector
            actions = self.Q_eval.forward(state)
            print(state.shape, actions.shape, actions)
            action = torch.argmax(actions).item()
        else:
            # epsilon概率执行随机动作
            action = np.random.choice(self.n_actions)
            print("random action:", action)
        return action

    # 从记忆中抽取batch进行学习
    def learn(self):
        # memory counter小于一个batch大小的时候直接return
        if self.mem_cntr < self.batch_size:
            print("learn:watching")
            return

        # 初始化梯度0
        self.Q_eval.optimizer.zero_grad()

        # 得到memory大小，不超过mem_size
        max_mem = min(self.mem_cntr, self.mem_size)

        # 随机生成一个batch的memory index，可重复抽取
        batch = np.random.choice(max_mem, self.batch_size, replace=False)
        batch_index = np.arange(self.batch_size, dtype=np.int32)

        # 从state memory中抽取一个batch
        state_batch = torch.tensor(self.state_memory[batch]).to(self.Q_eval.device)
        new_state_batch = torch.tensor(self.new_state_memory[batch]).to(self.Q_eval.device)
        reward_batch = torch.tensor(self.reward_memory[batch]).to(self.Q_eval.device)
        terminal_batch = torch.tensor(self.terminal_memory[batch]).to(self.Q_eval.device)  # 存储是否结束的bool型变量

        # action_batch = torch.tensor(self.action_memory[batch]).to(self.Q_eval.device)
        action_batch = self.action_memory[batch]

        # 第batch_index行，取action_batch列,对state_batch中的每一组输入，输出action对应的Q值,batchsize行，1列的Q值
        q_eval = self.Q_eval.forward(state_batch)[batch_index, action_batch]
        q_next = self.Q_eval.forward(new_state_batch)  # (64, 10) -> (64, 3)
        q_next[terminal_batch] = 0.0  # 如果是最终状态，则将q值置为0
        q_target = reward_batch + self.gamma * torch.max(q_next, dim=1)[0]

        loss = self.Q_eval.loss(q_target, q_eval).to(self.Q_eval.device)
        loss.backward()
        self.Q_eval.optimizer.step()

        self.epsilon = self.epsilon - self.eps_dec \
            if self.epsilon > self.eps_min else self.eps_min


def run_dqn():
    environ = Environment()
    agent = Agent(gamma=0.9, epsilon=1.0, lr=0.003, input_dims=10, batch_size=64, n_actions=3, eps_min=0.03)
    profits, eps_history = [], []
    epochs = 100

    for i in range(epochs):
        profit = 0
        done = False
        # can add env_list if have multiple stocks
        observation = environ.reset()
        while not done:
            print('barpos: ', environ.barpos)
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