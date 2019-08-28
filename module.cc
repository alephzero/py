#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

#include "packet.h"
#include "pubsub.h"
#include "rpc.h"
#include "shmobj.h"
#include "topic_manager.h"

namespace py = pybind11;

PYBIND11_MODULE(alephzero, m) {
  py::class_<a0_shmobj_t> pyshmobj(m, "ShmObj");

  py::class_<a0_shmobj_options_t>(pyshmobj, "Options")
      .def(py::init<>())
      .def(py::init([](off_t size) {
             return a0_shmobj_options_t{size};
           }),
           py::arg("size"))
      .def_readwrite("size", &a0_shmobj_options_t::size);

  pyshmobj
      .def(py::init(&ShmObjWrapper::open))
      .def("close", &ShmObjWrapper::close)
      .def_static("unlink", &ShmObjWrapper::unlink);

  py::class_<PacketWrapper>(m, "Packet")
      .def(py::init(&PacketWrapper::build))
      .def_property_readonly("headers", &PacketWrapper::headers)
      .def_property_readonly("payload", &PacketWrapper::payload)
      .def_property_readonly("id", &PacketWrapper::id);

  py::class_<a0_publisher_t>(m, "Publisher")
      .def(py::init(&PublisherWrapper::init))
      .def("close", &PublisherWrapper::close)
      .def("pub", &PublisherWrapper::pub);

  py::enum_<a0_subscriber_init_t>(m, "SubscriberInit")
      .value("INIT_OLDEST", A0_INIT_OLDEST)
      .value("INIT_MOST_RECENT", A0_INIT_MOST_RECENT)
      .value("INIT_AWAIT_NEW", A0_INIT_AWAIT_NEW)
      .export_values();

  py::enum_<a0_subscriber_iter_t>(m, "SubscriberIter")
      .value("ITER_NEXT", A0_ITER_NEXT)
      .value("ITER_NEWEST", A0_ITER_NEWEST)
      .export_values();

  py::class_<SubscriberSyncWrapper>(m, "SubscriberSync")
      .def(py::init(&SubscriberSyncWrapper::init))
      .def("close", &SubscriberSyncWrapper::close)
      .def("has_next", &SubscriberSyncWrapper::has_next)
      .def("next", &SubscriberSyncWrapper::next);

  py::class_<SubscriberWrapper>(m, "Subscriber")
      .def(py::init(&SubscriberWrapper::init))
      .def("close", &SubscriberWrapper::close)
      .def("async_close", &SubscriberWrapper::async_close);

  py::class_<RpcServerWrapper>(m, "RpcServer")
      .def(py::init(&RpcServerWrapper::init))
      .def("close", &RpcServerWrapper::close)
      .def("async_close", &RpcServerWrapper::async_close)
      .def("reply", &RpcServerWrapper::reply);

  py::class_<RpcClientWrapper>(m, "RpcClient")
      .def(py::init(&RpcClientWrapper::init))
      .def("close", &RpcClientWrapper::close)
      .def("async_close", &RpcClientWrapper::async_close)
      .def("send", &RpcClientWrapper::send)
      .def("cancel", &RpcClientWrapper::cancel);

  py::class_<a0_topic_manager_t>(m, "TopicManager")
      .def(py::init(&TopicManagerWrapper::init_jsonstr))
      .def("close", &TopicManagerWrapper::close)
      .def("open_config_topic", &TopicManagerWrapper::open_config_topic)
      .def("open_publisher_topic", &TopicManagerWrapper::open_publisher_topic)
      .def("open_subscriber_topic", &TopicManagerWrapper::open_subscriber_topic)
      .def("open_rpc_server_topic", &TopicManagerWrapper::open_rpc_server_topic)
      .def("open_rpc_client_topic", &TopicManagerWrapper::open_rpc_client_topic);
}
