from gym.envs.registration import register

register(
    id='spider-v1',
    entry_point='gym_spider.gym_spider.envs:SpiderEnv',
)