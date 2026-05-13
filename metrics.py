import sys
sys.path.insert(0, '.')
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

ratings = pd.read_csv('data/user_ratings.csv')
train, test = train_test_split(ratings, test_size=0.2, random_state=42)

print('=' * 60)
print('   ANTIGRAVITY - FULL METRICS REPORT')
print('=' * 60)
print('Training samples : ' + str(len(train)))
print('Test samples     : ' + str(len(test)))

mean_rating = train['Rating'].mean()
test = test.copy()
test['Predicted'] = mean_rating

mae  = np.mean(np.abs(test['Rating'] - test['Predicted']))
rmse = np.sqrt(np.mean((test['Rating'] - test['Predicted'])**2))
ss_res = np.sum((test['Rating'] - test['Predicted'])**2)
ss_tot = np.sum((test['Rating'] - test['Rating'].mean())**2)
r2 = 1 - (ss_res / ss_tot)

print('')
print('[REGRESSION METRICS]')
print('  MAE  (lower=better) : ' + str(round(mae, 4)))
print('  RMSE (lower=better) : ' + str(round(rmse, 4)))
print('  R2   (higher=better): ' + str(round(r2, 4)))

K = 5
precisions, recalls, ndcgs = [], [], []
for user_id in test['UserID'].unique():
    user_test = test[test['UserID'] == user_id]
    user_train = train[train['UserID'] == user_id]
    if len(user_test) == 0:
        continue
    relevant = set(user_test[user_test['Rating'] >= 4]['ProductID'])
    all_products = ratings['ProductID'].unique()
    rated = set(user_train['ProductID'])
    candidates = [p for p in all_products if p not in rated]
    np.random.seed(42)
    top_k = list(np.random.choice(candidates, min(K, len(candidates)), replace=False))
    hits = len(set(top_k) & relevant)
    precisions.append(hits / K)
    recalls.append(hits / len(relevant) if relevant else 0)
    dcg = sum([1/np.log2(i+2) for i, p in enumerate(top_k) if p in relevant])
    idcg = sum([1/np.log2(i+2) for i in range(min(len(relevant), K))])
    ndcgs.append(dcg/idcg if idcg > 0 else 0)

print('')
print('[RANKING METRICS @ K=5]')
print('  Precision@5 : ' + str(round(np.mean(precisions), 4)))
print('  Recall@5    : ' + str(round(np.mean(recalls), 4)))
print('  NDCG@5      : ' + str(round(np.mean(ndcgs), 4)))

print('')
print('[COVERAGE]')
print('  Users in test    : ' + str(test['UserID'].nunique()))
print('  Products in test : ' + str(test['ProductID'].nunique()))
print('  Catalogue size   : ' + str(ratings['ProductID'].nunique()))
print('  Coverage         : ' + str(round(test['ProductID'].nunique() / ratings['ProductID'].nunique() * 100, 1)) + '%')
print('=' * 60)
