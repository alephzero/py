#include <a0.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>

namespace py = pybind11;

template <typename T>
struct NoGilDeleter {
  void operator()(T* t) {
    py::gil_scoped_release nogil;
    delete t;
  }
};

template <typename T>
using nogil_holder = std::unique_ptr<T, NoGilDeleter<T>>;

PYBIND11_MODULE(alephzero_bindings, m) {
  py::class_<a0::File> pyfile(m, "File");

  py::class_<a0::Arena>(m, "Arena")
      .def(py::init<a0::File>())
      .def_property_readonly("size", &a0::Arena::size);

  py::implicitly_convertible<a0::File, a0::Arena>();

  py::class_<a0::File::Options> pyfileopts(pyfile, "Options");

  py::class_<a0::File::Options::CreateOptions>(pyfileopts, "CreateOptions")
      .def_readwrite("size", &a0::File::Options::CreateOptions::size)
      .def_readwrite("mode", &a0::File::Options::CreateOptions::mode)
      .def_readwrite("dir_mode", &a0::File::Options::CreateOptions::dir_mode);

  py::class_<a0::File::Options::OpenOptions>(pyfileopts, "OpenOptions")
      .def_readwrite("readonly", &a0::File::Options::OpenOptions::readonly);

  pyfileopts
      .def(py::init<>())
      .def_readwrite("create_options", &a0::File::Options::create_options)
      .def_readwrite("open_options", &a0::File::Options::open_options)
      .def_readonly_static("DEFAULT", &a0::File::Options::DEFAULT);

  pyfile
      .def(py::init<std::string_view>())
      .def(py::init<std::string_view, a0::File::Options>())
      .def_property_readonly("size", &a0::File::size)
      .def_property_readonly("path", &a0::File::path)
      .def_property_readonly("id", &a0::File::fd)
      .def_static("remove", &a0::File::remove)
      .def_static("remove_all", &a0::File::remove_all);

  py::class_<a0::PacketView>(m, "PacketView")
      .def(py::init<const a0::Packet&>())
      .def_property_readonly("id", &a0::PacketView::id)
      .def_property_readonly("headers", &a0::PacketView::headers)
      .def_property_readonly("payload", [](a0::PacketView* self) {
        return py::bytes(self->payload().data(), self->payload().size());
      });

  py::class_<a0::Packet>(m, "Packet")
      .def(py::init<>())
      .def(py::init<std::string>())
      .def(py::init<std::vector<std::pair<std::string, std::string>>, std::string>())
      .def(py::init<const a0::PacketView&>())
      .def_property_readonly("id", &a0::Packet::id)
      .def_property_readonly("headers", &a0::Packet::headers)
      .def_property_readonly("payload", [](a0::Packet* self) {
        return py::bytes(self->payload().data(), self->payload().size());
      });

  py::implicitly_convertible<a0::Packet, a0::PacketView>();

  py::class_<a0::TopicAliasTarget>(m, "TopicAliasTarget")
      .def(py::init<std::string, std::string>(), py::arg("container"), py::arg("topic"))
      .def(py::init([](py::dict d) {
        return a0::TopicAliasTarget{d["container"].cast<std::string>(),
                                    d["topic"].cast<std::string>()};
      }))
      .def_readwrite("container", &a0::TopicAliasTarget::container)
      .def_readwrite("topic", &a0::TopicAliasTarget::topic);

  py::implicitly_convertible<py::dict, a0::TopicAliasTarget>();

  using TopicAliasMap = std::map<std::string, a0::TopicAliasTarget>;
  py::bind_map<TopicAliasMap>(m, "TopicAliasMap");

  py::class_<a0::TopicManager>(m, "TopicManager")
      .def(py::init<std::string, TopicAliasMap, TopicAliasMap, TopicAliasMap>(),
           py::arg("container") = "",
           py::arg("subscriber_aliases") = TopicAliasMap{},
           py::arg("rpc_client_aliases") = TopicAliasMap{},
           py::arg("prpc_client_aliases") = TopicAliasMap{})
      .def(py::init([](py::dict d) {
        TopicAliasMap subscriber_aliases;
        TopicAliasMap rpc_client_aliases;
        TopicAliasMap prpc_client_aliases;
        if (d.contains("subscriber_aliases")) {
          subscriber_aliases = d["subscriber_aliases"].cast<TopicAliasMap>();
        }
        if (d.contains("rpc_client_aliases")) {
          rpc_client_aliases = d["rpc_client_aliases"].cast<TopicAliasMap>();
        }
        if (d.contains("prpc_client_aliases")) {
          prpc_client_aliases = d["prpc_client_aliases"].cast<TopicAliasMap>();
        }
        return a0::TopicManager{d["container"].cast<std::string>(),
                                subscriber_aliases,
                                rpc_client_aliases,
                                prpc_client_aliases};
      }))
      .def_readwrite("container", &a0::TopicManager::container)
      .def_readwrite("subscriber_aliases", &a0::TopicManager::subscriber_aliases)
      .def_readwrite("rpc_client_aliases", &a0::TopicManager::rpc_client_aliases)
      .def_readwrite("prpc_client_aliases", &a0::TopicManager::prpc_client_aliases)
      .def("config_topic", &a0::TopicManager::config_topic)
      .def("heartbeat_topic", &a0::TopicManager::heartbeat_topic)
      .def("log_crit_topic", &a0::TopicManager::log_crit_topic)
      .def("log_err_topic", &a0::TopicManager::log_err_topic)
      .def("log_warn_topic", &a0::TopicManager::log_warn_topic)
      .def("log_info_topic", &a0::TopicManager::log_info_topic)
      .def("log_dbg_topic", &a0::TopicManager::log_dbg_topic)
      .def("publisher_topic", &a0::TopicManager::publisher_topic)
      .def("subscriber_topic", &a0::TopicManager::subscriber_topic)
      .def("rpc_server_topic", &a0::TopicManager::rpc_server_topic)
      .def("rpc_client_topic", &a0::TopicManager::rpc_client_topic)
      .def("prpc_server_topic", &a0::TopicManager::prpc_server_topic)
      .def("prpc_client_topic", &a0::TopicManager::prpc_client_topic);

  py::implicitly_convertible<py::dict, a0::TopicManager>();

  m.def("InitGlobalTopicManager", &a0::InitGlobalTopicManager);
  m.def("GlobalTopicManager", &a0::GlobalTopicManager);

  py::class_<a0::Publisher>(m, "Publisher")
      .def(py::init<a0::Arena>())
      .def(py::init<std::string_view>())
      .def("pub", py::overload_cast<const a0::PacketView&>(&a0::Publisher::pub))
      .def("pub",
           py::overload_cast<std::vector<std::pair<std::string, std::string>>,
                             std::string_view>(&a0::Publisher::pub))
      .def("pub", py::overload_cast<std::string_view>(&a0::Publisher::pub));

  py::enum_<a0_subscriber_init_t>(m, "SubscriberInit")
      .value("INIT_OLDEST", A0_INIT_OLDEST)
      .value("INIT_MOST_RECENT", A0_INIT_MOST_RECENT)
      .value("INIT_AWAIT_NEW", A0_INIT_AWAIT_NEW)
      .export_values();

  py::enum_<a0_subscriber_iter_t>(m, "SubscriberIter")
      .value("ITER_NEXT", A0_ITER_NEXT)
      .value("ITER_NEWEST", A0_ITER_NEWEST)
      .export_values();

  py::class_<a0::SubscriberSync>(m, "SubscriberSync")
      .def(py::init<a0::Arena, a0_subscriber_init_t, a0_subscriber_iter_t>())
      .def(py::init<std::string_view, a0_subscriber_init_t, a0_subscriber_iter_t>())
      .def("has_next", &a0::SubscriberSync::has_next)
      .def("next", &a0::SubscriberSync::next);

  py::class_<a0::Subscriber, nogil_holder<a0::Subscriber>>(m, "Subscriber")
      .def(py::init<a0::Arena,
                    a0_subscriber_init_t,
                    a0_subscriber_iter_t,
                    std::function<void(a0::PacketView)>>())
      .def(py::init<std::string_view,
                    a0_subscriber_init_t,
                    a0_subscriber_iter_t,
                    std::function<void(a0::PacketView)>>())
      .def("async_close", &a0::Subscriber::async_close)
      .def_static("read_one",
                  py::overload_cast<a0::Arena, a0_subscriber_init_t, int>(
                      &a0::Subscriber::read_one),
                  py::arg("arena"),
                  py::arg("seek"),
                  py::arg("flags") = 0)
      .def_static("read_one",
                  py::overload_cast<std::string_view, a0_subscriber_init_t, int>(
                      &a0::Subscriber::read_one),
                  py::arg("topic"),
                  py::arg("seek"),
                  py::arg("flags") = 0);

  m.def("read_config", &a0::read_config, py::arg("flags") = 0);

  py::class_<a0::RpcRequest>(m, "RpcRequest")
      .def_property_readonly("pkt", &a0::RpcRequest::pkt)
      .def("reply", py::overload_cast<const a0::PacketView&>(&a0::RpcRequest::reply))
      .def("reply",
           py::overload_cast<std::vector<std::pair<std::string, std::string>>,
                             std::string_view>(&a0::RpcRequest::reply))
      .def("reply", py::overload_cast<std::string_view>(&a0::RpcRequest::reply));

  py::class_<a0::RpcServer, nogil_holder<a0::RpcServer>>(m, "RpcServer")
      .def(py::init<a0::Arena,
                    std::function<void(a0::RpcRequest)>,
                    std::function<void(std::string_view)>>())
      .def(py::init<std::string_view,
                    std::function<void(a0::RpcRequest)>,
                    std::function<void(std::string_view)>>())
      .def("async_close", &a0::RpcServer::async_close);

  py::class_<a0::RpcClient, nogil_holder<a0::RpcClient>>(m, "RpcClient")
      .def(py::init<a0::Arena>())
      .def(py::init<std::string_view>())
      .def("async_close", &a0::RpcClient::async_close)
      .def("send",
           py::overload_cast<const a0::PacketView&, std::function<void(const a0::PacketView&)>>(
               &a0::RpcClient::send))
      .def("send",
           py::overload_cast<std::vector<std::pair<std::string, std::string>>,
                             std::string_view,
                             std::function<void(const a0::PacketView&)>>(&a0::RpcClient::send))
      .def("send",
           py::overload_cast<std::string_view, std::function<void(const a0::PacketView&)>>(
               &a0::RpcClient::send))
      .def("cancel", &a0::RpcClient::cancel);

  py::class_<a0::PrpcConnection>(m, "PrpcConnection")
      .def_property_readonly("pkt", &a0::PrpcConnection::pkt)
      .def("send", py::overload_cast<const a0::PacketView&, bool>(&a0::PrpcConnection::send))
      .def("send",
           py::overload_cast<std::vector<std::pair<std::string, std::string>>,
                             std::string_view,
                             bool>(&a0::PrpcConnection::send))
      .def("send", py::overload_cast<std::string_view, bool>(&a0::PrpcConnection::send));

  py::class_<a0::PrpcServer, nogil_holder<a0::PrpcServer>>(m, "PrpcServer")
      .def(py::init<a0::Arena,
                    std::function<void(a0::PrpcConnection)>,
                    std::function<void(std::string_view)>>())
      .def(py::init<std::string_view,
                    std::function<void(a0::PrpcConnection)>,
                    std::function<void(std::string_view)>>())
      .def("async_close", &a0::PrpcServer::async_close);

  py::class_<a0::PrpcClient, nogil_holder<a0::PrpcClient>>(m, "PrpcClient")
      .def(py::init<a0::Arena>())
      .def(py::init<std::string_view>())
      .def("async_close", &a0::PrpcClient::async_close)
      .def("connect",
           py::overload_cast<const a0::PacketView&,
                             std::function<void(const a0::PacketView&, bool)>>(
               &a0::PrpcClient::connect))
      .def("connect",
           py::overload_cast<std::vector<std::pair<std::string, std::string>>,
                             std::string_view,
                             std::function<void(const a0::PacketView&, bool)>>(
               &a0::PrpcClient::connect))
      .def("connect",
           py::overload_cast<std::string_view,
                             std::function<void(const a0::PacketView&, bool)>>(
               &a0::PrpcClient::connect))
      .def("cancel", &a0::PrpcClient::cancel);

  py::class_<a0::Heartbeat> pyheartbeat(m, "Heartbeat");

  py::class_<a0::Heartbeat::Options>(pyheartbeat, "Options")
      .def(py::init<>())
      .def(py::init([](double freq) {
             return a0::Heartbeat::Options{freq};
           }),
           py::arg("freq"))
      .def_readwrite("freq", &a0::Heartbeat::Options::freq)
      .def_readonly_static("DEFAULT", &a0::Heartbeat::Options::DEFAULT);

  pyheartbeat
      .def(py::init<a0::Arena, a0::Heartbeat::Options>(), py::arg("shm"), py::arg("options"))
      .def(py::init<a0::Arena>(), py::arg("shm"))
      .def(py::init<a0::Heartbeat::Options>(), py::arg("options"))
      .def(py::init());

  py::class_<a0::HeartbeatListener, nogil_holder<a0::HeartbeatListener>>
  pyheartbeatlistener(m, "HeartbeatListener");

  py::class_<a0::HeartbeatListener::Options>(pyheartbeatlistener, "Options")
      .def(py::init<>())
      .def(py::init([](double min_freq) {
             return a0::HeartbeatListener::Options{min_freq};
           }),
           py::arg("min_freq"))
      .def_readwrite("min_freq", &a0::HeartbeatListener::Options::min_freq)
      .def_readonly_static("DEFAULT", &a0::HeartbeatListener::Options::DEFAULT);

  pyheartbeatlistener
      .def(py::init<a0::Arena, a0::HeartbeatListener::Options, std::function<void()>, std::function<void()>>(),
           py::arg("shm"), py::arg("options"), py::arg("ondetected"), py::arg("onmissed"))
      .def(py::init<a0::Arena, std::function<void()>, std::function<void()>>(),
           py::arg("shm"), py::arg("ondetected"), py::arg("onmissed"))
      .def(py::init<std::string_view, a0::HeartbeatListener::Options, std::function<void()>, std::function<void()>>(),
           py::arg("container"), py::arg("options"), py::arg("ondetected"), py::arg("onmissed"))
      .def(py::init<std::string_view, std::function<void()>, std::function<void()>>(),
           py::arg("container"), py::arg("ondetected"), py::arg("onmissed"))
      .def(py::init<a0::HeartbeatListener::Options, std::function<void()>, std::function<void()>>(),
           py::arg("options"), py::arg("ondetected"), py::arg("onmissed"))
      .def(py::init<std::function<void()>, std::function<void()>>(),
           py::arg("ondetected"), py::arg("onmissed"))
      .def("async_close", &a0::HeartbeatListener::async_close);
}
