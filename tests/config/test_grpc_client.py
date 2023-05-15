from config.grpc_client import GrpcSingletonChannel, SingletonMeta


def test_grpc_singleton_channel_should_implements_singleton_meta():
    assert isinstance(GrpcSingletonChannel, SingletonMeta)


def test_grpc_singleton_channel_instance_should_return_same_instance_for_each_call_implementing_singleton_pattern():
    class SimpleClass:
        def __init__(self):
            pass

    sc1 = SimpleClass()
    sc2 = SimpleClass()
    simple_class_has_different_instances = sc1 is not sc2

    gc1 = GrpcSingletonChannel()
    gc2 = GrpcSingletonChannel()
    singleton_class_has_the_same_instance = gc1 is gc2

    assert simple_class_has_different_instances
    assert singleton_class_has_the_same_instance
