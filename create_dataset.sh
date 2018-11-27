mkdir $1/datasets

ln -s $1/tcga_ssgsea_train.txt $1/datasets/train.txt
ln -s $1/tcga_ssgsea_test.txt $1/datasets/test.txt
ln -s $1/tcga_ssgsea_val.txt $1/datasets/val.txt
ln -s $1/tcga_survival_eval.txt $1/datasets/val_survival.txt
ln -s $1/tcga_survival_test.txt $1/datasets/test_survival.txt
ln -s $1/tcga_survival_train.txt $1/datasets/train_survival.txt