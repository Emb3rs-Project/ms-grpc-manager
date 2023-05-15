from config.grpc_client import GrpcChannel, SingletonMeta


def test_grpc_channel_should_implements_singleton_meta():
    assert isinstance(GrpcChannel, SingletonMeta)


def test_grpc_channel_instance_should_return_same_instance_for_each_call_implementing_singleton_pattern():
    class SimpleClass:
        def __init__(self):
            pass

    sc1 = SimpleClass()
    sc2 = SimpleClass()
    simple_class_has_different_instances = sc1 is not sc2

    gc1 = GrpcChannel()
    gc2 = GrpcChannel()
    singleton_class_has_the_same_instance = gc1 is gc2

    assert simple_class_has_different_instances
    assert singleton_class_has_the_same_instance
