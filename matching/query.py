import time
import grpc
import matching.match_service_pb2 as match_service_pb2
import matching.match_service_pb2_grpc as match_service_pb2_grpc

class MatchingQueryClient:
    def __init__(self, matching_engine_service_ip, deployed_index_id):
        self._ip_addr = matching_engine_service_ip
        channel = grpc.insecure_channel("{}:10000".format(self._ip_addr))
        self._stub = match_service_pb2_grpc.MatchServiceStub(channel)
        self._deployed_index_id = deployed_index_id

    def tfmodel(self):
        import tensorflow as tf
        import tensorflow_hub as hub
        if self.model is None:
            self._model = tf.keras.Sequential([hub.KerasLayer("https://tfhub.dev/google/imagenet/mobilenet_v2_100_224/feature_vector/5", trainable=False)])
            self._model.build([None, 224, 224, 3])  # Batch input shape.

        return self._model

    def query_embedding(self, embedding):
        request = match_service_pb2.MatchRequest()
        request.deployed_index_id = self._deployed_index_id
        for v in embedding:
            request.float_val.append(v)
        request.num_neighbors = 30

        st = time.time()
        response = self._stub.Match(request)
        ed = time.time()
        return (response, ed - st)

    def query_image(self, jpeg_file):
        import tensorflow as tf
        from io import BytesIO
        from PIL import Image
        with tf.io.gfile.GFile(jpeg_file, "rb") as f:
            buf = f.read()
        img = Image.open(BytesIO(buf))
        img = img.resize((224, 224), Image.BICUBIC)
        buf = BytesIO()
        img.save(buf, "JPEG")
        input_tensor = tf.reshape(tf.io.decode_jpeg(buf.getvalue(), channels=3), (1, 224, 224, 3))
        embedding = self.tfmodel().predict({"inputs": input_tensor})[0].tolist()
        return self.query_embedding(embedding)

