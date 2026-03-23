import time
import os

class ExperimentTracker:
    def __init__(self, experiment_name: str = "capital-one-ai-assistant"):
        self.experiment_name = experiment_name
        self._mlflow_available = False
        self._setup_mlflow()

    def _setup_mlflow(self):
        """Tries to connect to MLflow, disables tracking gracefully if unavailable."""
        try:
            import mlflow
            # Using a local SQLite backend for demo purposes if no URI is provided
            mlflow.set_tracking_uri(os.environ.get('MLFLOW_TRACKING_URI', 'sqlite:///mlflow.db'))
            mlflow.set_experiment(self.experiment_name)
            self._mlflow = mlflow
            self._mlflow_available = True
            print(f"MLflow tracking enabled for experiment: {self.experiment_name}")
        except Exception as e:
            print(f"MLflow unavailable, tracking disabled: {e}")

    def log_query_metrics(self, query: str, response: str, latency: float, safety_status: str, quality_score: float = 0.85):
        """
        Logs comprehensive metrics for a single RAG query.
        """
        if not self._mlflow_available:
            print(f"[MLflow Offline] Query: {query} | Latency: {latency:.2f}s | Safety: {safety_status}")
            return

        try:
            with self._mlflow.start_run(run_name=f"query-{int(time.time())}"):
                self._mlflow.log_param("query", query)
                self._mlflow.log_metric("latency_ms", int(latency * 1000))
                self._mlflow.log_metric("quality_score", quality_score)
                self._mlflow.log_param("safety_status", safety_status)
                # Cost estimation for small local models (mostly compute power)
                self._mlflow.log_metric("est_token_cost", 0.00001) 
        except Exception as e:
            print(f"Error logging to MLflow: {e}")

    def track_latency(self, func_name: str, duration: float):
        if not self._mlflow_available:
            return
        try:
            with self._mlflow.start_run(run_name=f"latency-{func_name}", nested=True):
                self._mlflow.log_metric("duration_seconds", duration)
        except Exception:
            pass

    def log_retrieval_success(self, query: str, context_length: int):
        if not self._mlflow_available:
            return
        try:
            with self._mlflow.start_run(run_name="retrieval-step", nested=True):
                self._mlflow.log_param("query", query)
                self._mlflow.log_metric("context_length", context_length)
        except Exception:
            pass
