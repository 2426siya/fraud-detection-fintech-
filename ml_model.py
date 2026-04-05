import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

def generate_training_data(n_samples: int = 5000):
    np.random.seed(42)
    X_legit = np.column_stack([
        np.random.uniform(10, 500, n_samples),
        np.random.choice(range(8, 22), n_samples),
        np.zeros(n_samples),
        np.random.randint(0, 3, n_samples),
        np.random.uniform(0, 50, n_samples),
        np.random.uniform(0.5, 2.0, n_samples),
        np.random.choice([0, 1], n_samples, p=[0.8, 0.2]),
        np.random.choice([0, 1, 2], n_samples),
    ])
    y_legit = np.zeros(n_samples)

    X_fraud = np.column_stack([
        np.random.uniform(500, 5000, n_samples),
        np.random.choice(list(range(0, 6)) + list(range(22, 24)), n_samples),
        np.ones(n_samples),
        np.random.randint(5, 15, n_samples),
        np.random.uniform(200, 5000, n_samples),
        np.random.uniform(3.0, 20.0, n_samples),
        np.ones(n_samples),
        np.random.choice([2, 3], n_samples),
    ])
    y_fraud = np.ones(n_samples)

    X = np.vstack([X_legit, X_fraud])
    y = np.concatenate([y_legit, y_fraud])

    idx = np.random.permutation(len(X))
    return X[idx], y[idx]


class FraudMLModel:
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            min_samples_leaf=5,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        )
        self.scaler  = StandardScaler()
        self.trained = False
        self._train()

    def _train(self):
        X, y = generate_training_data()
        X_scaled = self.scaler.fit_transform(X)
        self.model.fit(X_scaled, y)
        self.trained = True
        print("[ML] RandomForest fraud model trained on 10,000 synthetic samples.")

    def predict(self, features: list) -> float:
        if not self.trained:
            return 0.5
        arr = np.array(features).reshape(1, -1)
        arr_scaled = self.scaler.transform(arr)
        proba = self.model.predict_proba(arr_scaled)[0]
        return float(proba[1]) if len(proba) > 1 else float(proba[0])


fraud_ml_model = FraudMLModel()