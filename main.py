from argparse import ArgumentParser

import pytorch_lightning as pl
import pytorch_lightning.callbacks as plc
from pytorch_lightning import Trainer
from pytorch_lightning.loggers import TensorBoardLogger

from data import DInterface
from model import MInterface
from utils import load_model_path_by_args


def load_callbacks():
    callbacks = [
        plc.ModelCheckpoint(
            monitor='val_acc',
            filename='best-{epoch:02d}-{val_acc:.3f}',
            save_top_k=2,
            auto_insert_metric_name=True,
            mode='max',
            save_last=True
        ), ]
    if args.lr_scheduler:
        print("Load the LearningRateMonitor")
        callbacks.append(plc.LearningRateMonitor(logging_interval='epoch'))
    return callbacks


def main(args):
    pl.seed_everything(args.seed)
    load_path = load_model_path_by_args(args)
    data_module = DInterface(**vars(args))

    if load_path is None:
        model = MInterface(**vars(args))
    else:
        model = MInterface(**vars(args))
        args.resume_from_checkpoint = load_path
        logger = TensorBoardLogger(save_dir='./', name='lightning_logs', version=args.version)
        args.logger = logger
    args.callbacks = load_callbacks()
    # logger = TensorBoardLogger(save_dir=args.logdir_path, name=args.log_dir)
    # args.logger = logger
    # Trainer(auto_scale_batch_size=, auto_lr_find=)
    # os.environ["CUDA_VISIBLE_DEVICES"] = '0,1'
    trainer = Trainer.from_argparse_args(args, gpus=1, precision=16)

    # trainer.tune(model, data_module)
    # print('the new lr is :', model.hparams.lr)

    # Trainer(limit_val_batches=2, fast_dev_run=True, limit_train_batches=)
    # trainer = Trainer.from_argparse_args(args, gpus=2, precision=16, strategy='ddp'
    #                                      , enable_progress_bar=False, )
    trainer.fit(model, data_module, )


if __name__ == '__main__':
    parser = ArgumentParser()

    # Basic Training Control
    parser.add_argument('--batch_size', default=512, type=int)
    parser.add_argument('--num_workers', default=16, type=int)
    parser.add_argument('--seed', default=2022, type=int)
    parser.add_argument('--lr', default=0.0001445439770745928 * 2, type=float)

    # LR Scheduler
    parser.add_argument('--lr_scheduler', choices=['step', 'cosine'], type=str)
    parser.add_argument('--lr_decay_steps', default=100, type=int)
    parser.add_argument('--lr_decay_rate', default=0.5, type=float)
    parser.add_argument('--lr_decay_min_lr', default=1e-5, type=float)

    # Restart Control
    parser.add_argument('--load_best', action='store_true')
    parser.add_argument('--load_dir', default=None, type=str)
    parser.add_argument('--load_ver', default=None, type=str)
    parser.add_argument('--load_v_num', default=None, type=int)

    # Training Infoe
    parser.add_argument('--dataset', default='image_dataset', type=str)
    parser.add_argument('--data_dir', default='/home/pyz/data/COCO', type=str)
    parser.add_argument('--model_name', default='model_image_distilled', type=str)
    parser.add_argument('--teacher_name', default='ViT-B/32', type=str)
    parser.add_argument('--loss', default=['kl', 'l1'], nargs='+', type=list)
    parser.add_argument('--weight_decay', default=1e-5, type=float)
    parser.add_argument('--no_augment', action='store_true')
    parser.add_argument('--log_dir', default='runs', type=str)
    parser.add_argument('--cache_dir', default='cache', type=str)

    # Vit Model Hyperparameters
    parser.add_argument('--input_resolution', default=224, type=int)
    parser.add_argument('--patch_size', default=32, type=int)
    parser.add_argument('--width', default=384, type=int)
    parser.add_argument('--layers', default=6, type=int)
    parser.add_argument('--heads', default=24, type=int)

    # Transformer Model Hyperparameters
    """
     context_length, vocab_size, transformer_width, transformer_layers, transformer_heads, output_dim
    """
    parser.add_argument('--context_length', default=77, type=int)
    parser.add_argument('--vocab_size', default=49408, type=int)
    parser.add_argument('--transformer_width', default=128, type=int)
    parser.add_argument('--transformer_layers', default=6, type=int)
    parser.add_argument('--transformer_heads', default=8, type=int)

    # share Hyperparameters
    parser.add_argument('--output_dim', default=512, type=int)

    # Other
    parser.add_argument('--aug_prob', default=0.5, type=float)

    # Distilled Hyperparameters
    parser.add_argument('--t', default=4, type=int)
    parser.add_argument('--weight', default=[0.5, 0.5], nargs='+', type=list)
    parser.add_argument('--loss_scale', default=[10, 1], nargs='+', type=list)

    # Add pytorch lightning's args to parser as a group.
    # parser = Trainer.add_argparse_args(parser)

    # Reset Some Default Trainer Arguments' Default Values
    parser.set_defaults(max_epochs=500)
    args = parser.parse_args()

    # List Arguments
    args.mean_sen = [0.485, 0.456, 0.406]
    args.std_sen = [0.229, 0.224, 0.225]

    for key, value in args.__dict__.items():
        print(key, ' : ', value)

    main(args)
