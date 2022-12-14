# mkdir $1/datasets
# ln -s $1/survival.data.txt $1/datasets/train.txt
# ln -s $1/survival.data.txt $1/datasets/test.txt
# ln -s $1/survival.data.txt $1/datasets/val.txt
# ln -s $1/survival.train.txt $1/datasets/val_survival.txt
# ln -s $1/survival.train.txt $1/datasets/test_survival.txt
# ln -s $1/survival.train.txt $1/datasets/train_survival.txt

mkdir $1/datasets
ln -s $1/features.txt $1/datasets/ssgsea_train.txt
ln -s $1/features.txt $1/datasets/ssgsea_test.txt
ln -s $1/features.txt $1/datasets/ssgsea_val.txt
ln -s $1/outputs.train.txt $1/datasets/phenotype_train.txt
ln -s $1/outputs.train.txt $1/datasets/phenotype_test.txt
ln -s $1/outputs.train.txt $1/datasets/phenotype_val.txt
