import argparse
import d3rlpy
from sklearn.model_selection import train_test_split


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='hopper-medium-v0')
    parser.add_argument('--seed', type=int, default=1)
    parser.add_argument('--gpu', type=int)
    args = parser.parse_args()

    dataset, env = d3rlpy.datasets.get_dataset(args.dataset)

    # fix seed
    d3rlpy.seed(args.seed)
    env.seed(args.seed)

    _, test_episodes = train_test_split(dataset, test_size=0.2)

    vae_encoder = d3rlpy.models.encoders.VectorEncoderFactory([750, 750])
    rl_encoder = d3rlpy.models.encoders.VectorEncoderFactory([400, 300])

    bcq = d3rlpy.algos.BCQ(actor_encoder_factory=rl_encoder,
                           critic_encoder_factory=rl_encoder,
                           imitator_encoder_factory=vae_encoder,
                           use_gpu=args.gpu)

    bcq.fit(dataset.episodes,
            eval_episodes=test_episodes,
            n_steps=500000,
            n_steps_per_epoch=1000,
            save_interval=10,
            scorers={
                'environment': d3rlpy.metrics.evaluate_on_environment(env),
                'value_scale': d3rlpy.metrics.average_value_estimation_scorer,
            },
            experiment_name=f"BCQ_{args.dataset}_{args.seed}")


if __name__ == '__main__':
    main()
