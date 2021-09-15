#include <a0.h>
#include <pybind11/functional.h>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <pybind11/stl_bind.h>
#include <Python.h>

namespace py = pybind11;

#if (__cplusplus < 201703L)

namespace pybind11 {
namespace detail {

template <>
struct type_caster<a0::string_view> : string_caster<a0::string_view, true> {};

} // namespace detail
} // namespace pybind11

#endif

template <typename T>
struct NoGilDeleter {
  void operator()(T* t) {
    py::gil_scoped_release nogil;
    delete t;
  }
};

template <typename T>
using nogil_holder = std::unique_ptr<T, NoGilDeleter<T>>;

a0::string_view as_string_view(py::bytes& b) {
  char* data = nullptr;
  int64_t size = 0;
  PyBytes_AsStringAndSize(b.ptr(), &data, &size);
  return a0::string_view(data, size);
}

a0::string_view as_string_view(py::str& s) {
  int64_t size = 0;
  const char* data = PyUnicode_AsUTF8AndSize(s.ptr(), &size);
  return a0::string_view(data, size);
}

PYBIND11_MODULE(alephzero_bindings, m) {
  py::class_<a0::Arena> pyarena(m, "Arena");
  py::class_<a0::File> pyfile(m, "File");

  py::enum_<a0_arena_mode_t>(pyarena, "Mode")
      .value("SHARED", A0_ARENA_MODE_SHARED)
      .value("EXCLUSIVE", A0_ARENA_MODE_EXCLUSIVE)
      .value("READONLY", A0_ARENA_MODE_READONLY)
      .export_values();

  pyarena
      .def(py::init([](a0::File file) { return a0::Arena(file); }))
      .def_property_readonly("buf", [](a0::Arena& self) {
        return py::memoryview::from_memory(self.buf().data(), self.buf().size());
      })
      .def_property_readonly("mode", [](a0::Arena& self) { return self.mode(); });

  py::class_<a0::File::Options> pyfileopts(pyfile, "Options");

  py::class_<a0::File::Options::CreateOptions>(pyfileopts, "CreateOptions")
      .def_readwrite("size", &a0::File::Options::CreateOptions::size)
      .def_readwrite("mode", &a0::File::Options::CreateOptions::mode)
      .def_readwrite("dir_mode", &a0::File::Options::CreateOptions::dir_mode);

  py::class_<a0::File::Options::OpenOptions>(pyfileopts, "OpenOptions")
      .def_readwrite("arena_mode", &a0::File::Options::OpenOptions::arena_mode);

  pyfileopts
      .def(py::init<>())
      .def_readwrite("create_options", &a0::File::Options::create_options)
      .def_readwrite("open_options", &a0::File::Options::open_options)
      .def_static("DEFAULT", []() { return a0::File::Options::DEFAULT; });

  pyfile
      .def(py::init<a0::string_view>())
      .def(py::init<a0::string_view, a0::File::Options>())
      .def_property_readonly("arena", &a0::File::arena)
      .def_property_readonly("size", &a0::File::size)
      .def_property_readonly("path", &a0::File::path)
      .def_property_readonly("fd", &a0::File::fd)
      .def_property_readonly("stat", [](const a0::File& self) {
          auto stat = self.stat();
          auto os = py::module::import("os");
          return os.attr("stat_result")(py::make_tuple(
              stat.st_mode,
              stat.st_ino,
              stat.st_dev,
              stat.st_nlink,
              stat.st_uid,
              stat.st_gid,
              stat.st_size,
              stat.st_atime,
              stat.st_mtime,
              stat.st_ctime));
      })
      .def_static("remove", &a0::File::remove)
      .def_static("remove_all", &a0::File::remove_all);

  py::implicitly_convertible<a0::File, a0::Arena>();

  py::class_<a0::Packet>(m, "Packet")
      .def(py::init<>())
      .def(py::init([](py::bytes payload) {
        return a0::Packet(as_string_view(payload), a0::ref);
      }), py::keep_alive<0, 1>())
      .def(py::init([](std::vector<std::pair<std::string, std::string>> hdrs, py::bytes payload) {
        std::unordered_multimap<std::string, std::string> hdrs_map;
        for (auto& hdr : hdrs) {
          hdrs_map.insert({std::move(hdr.first), std::move(hdr.second)});
        }
        return a0::Packet(std::move(hdrs_map), as_string_view(payload), a0::ref);
      }), py::keep_alive<0, 2>())
      .def(py::init([](py::str payload) {
        return a0::Packet(as_string_view(payload), a0::ref);
      }), py::keep_alive<0, 1>())
      .def(py::init([](std::vector<std::pair<std::string, std::string>> hdrs, py::str payload) {
        std::unordered_multimap<std::string, std::string> hdrs_map;
        for (auto& hdr : hdrs) {
          hdrs_map.insert({std::move(hdr.first), std::move(hdr.second)});
        }
        return a0::Packet(std::move(hdrs_map), as_string_view(payload), a0::ref);
      }), py::keep_alive<0, 2>())
      .def_property_readonly("id", &a0::Packet::id)
      .def_property_readonly("headers", [](a0::Packet* self) {
          std::vector<std::pair<std::string, std::string>> ret;
          for (auto& hdr : self->headers()) {
            ret.push_back({hdr.first, hdr.second});
          }
          return ret;
      })
      .def_property_readonly("payload", [](a0::Packet* self) {
        return py::bytes(self->payload().data(), self->payload().size());
      })
      .def_property_readonly("payload_view", [](a0::Packet* self) {
        return py::memoryview::from_memory(self->payload().data(), self->payload().size());
      });

  py::class_<a0::Middleware>(m, "Middleware");
  m.def("add_time_mono_header", &a0::add_time_mono_header);
  m.def("add_time_wall_header", &a0::add_time_wall_header);
  m.def("add_writer_id_header", &a0::add_writer_id_header);
  m.def("add_writer_seq_header", &a0::add_writer_seq_header);
  m.def("add_transport_seq_header", &a0::add_transport_seq_header);
  m.def("add_standard_headers", &a0::add_standard_headers);

  py::class_<a0::Writer>(m, "Writer")
      .def(py::init<a0::Arena>())
      .def("write", py::overload_cast<a0::Packet>(&a0::Writer::write))
      .def("write", py::overload_cast<a0::string_view>(&a0::Writer::write))
      .def("push", &a0::Writer::push)
      .def("wrap", &a0::Writer::wrap);

  py::enum_<a0_reader_init_t>(m, "ReaderInit")
      .value("INIT_OLDEST", A0_INIT_OLDEST)
      .value("INIT_MOST_RECENT", A0_INIT_MOST_RECENT)
      .value("INIT_AWAIT_NEW", A0_INIT_AWAIT_NEW)
      .export_values();

  py::enum_<a0_reader_iter_t>(m, "ReaderIter")
      .value("ITER_NEXT", A0_ITER_NEXT)
      .value("ITER_NEWEST", A0_ITER_NEWEST)
      .export_values();

  py::class_<a0::ReaderSync>(m, "ReaderSync")
      .def(py::init<a0::Arena, a0_reader_init_t, a0_reader_iter_t>())
      .def("has_next", &a0::ReaderSync::has_next)
      .def("next", &a0::ReaderSync::next);

  py::class_<a0::Reader, nogil_holder<a0::Reader>>(m, "Reader")
      .def(py::init<a0::Arena,
                    a0_reader_init_t,
                    a0_reader_iter_t,
                    std::function<void(a0::Packet)>>())
      .def_static("read_one",
                  py::overload_cast<a0::Arena, a0_reader_init_t, int>(&a0::Reader::read_one),
                  py::arg("arena"),
                  py::arg("init"),
                  py::arg("flags") = 0);

//   py::class_<a0::Publisher>(m, "Publisher")
//       .def(py::init<a0::Arena>())
//       .def(py::init<a0::string_view>())
//       .def("pub", py::overload_cast<const a0::Packet&>(&a0::Publisher::pub))
//       .def("pub",
//            py::overload_cast<std::vector<std::pair<std::string, std::string>>,
//                              a0::string_view>(&a0::Publisher::pub))
//       .def("pub", py::overload_cast<a0::string_view>(&a0::Publisher::pub));

//   py::enum_<a0_subscriber_init_t>(m, "SubscriberInit")
//       .value("INIT_OLDEST", A0_INIT_OLDEST)
//       .value("INIT_MOST_RECENT", A0_INIT_MOST_RECENT)
//       .value("INIT_AWAIT_NEW", A0_INIT_AWAIT_NEW)
//       .export_values();

//   py::enum_<a0_subscriber_iter_t>(m, "SubscriberIter")
//       .value("ITER_NEXT", A0_ITER_NEXT)
//       .value("ITER_NEWEST", A0_ITER_NEWEST)
//       .export_values();

//   py::class_<a0::SubscriberSync>(m, "SubscriberSync")
//       .def(py::init<a0::Arena, a0_subscriber_init_t, a0_subscriber_iter_t>())
//       .def(py::init<a0::string_view, a0_subscriber_init_t, a0_subscriber_iter_t>())
//       .def("has_next", &a0::SubscriberSync::has_next)
//       .def("next", &a0::SubscriberSync::next);

//   py::class_<a0::Subscriber, nogil_holder<a0::Subscriber>>(m, "Subscriber")
//       .def(py::init<a0::Arena,
//                     a0_subscriber_init_t,
//                     a0_subscriber_iter_t,
//                     std::function<void(a0::Packet)>>())
//       .def(py::init<a0::string_view,
//                     a0_subscriber_init_t,
//                     a0_subscriber_iter_t,
//                     std::function<void(a0::Packet)>>())
//       .def("async_close", &a0::Subscriber::async_close)
//       .def_static("read_one",
//                   py::overload_cast<a0::Arena, a0_subscriber_init_t, int>(
//                       &a0::Subscriber::read_one),
//                   py::arg("arena"),
//                   py::arg("seek"),
//                   py::arg("flags") = 0)
//       .def_static("read_one",
//                   py::overload_cast<a0::string_view, a0_subscriber_init_t, int>(
//                       &a0::Subscriber::read_one),
//                   py::arg("topic"),
//                   py::arg("seek"),
//                   py::arg("flags") = 0);

//   m.def("read_config", &a0::read_config, py::arg("flags") = 0);

//   py::class_<a0::RpcRequest>(m, "RpcRequest")
//       .def_property_readonly("pkt", &a0::RpcRequest::pkt)
//       .def("reply", py::overload_cast<const a0::Packet&>(&a0::RpcRequest::reply))
//       .def("reply",
//            py::overload_cast<std::vector<std::pair<std::string, std::string>>,
//                              a0::string_view>(&a0::RpcRequest::reply))
//       .def("reply", py::overload_cast<a0::string_view>(&a0::RpcRequest::reply));

//   py::class_<a0::RpcServer, nogil_holder<a0::RpcServer>>(m, "RpcServer")
//       .def(py::init<a0::Arena,
//                     std::function<void(a0::RpcRequest)>,
//                     std::function<void(a0::string_view)>>())
//       .def(py::init<a0::string_view,
//                     std::function<void(a0::RpcRequest)>,
//                     std::function<void(a0::string_view)>>())
//       .def("async_close", &a0::RpcServer::async_close);

//   py::class_<a0::RpcClient, nogil_holder<a0::RpcClient>>(m, "RpcClient")
//       .def(py::init<a0::Arena>())
//       .def(py::init<a0::string_view>())
//       .def("async_close", &a0::RpcClient::async_close)
//       .def("send",
//            py::overload_cast<const a0::Packet&, std::function<void(const a0::Packet&)>>(
//                &a0::RpcClient::send))
//       .def("send",
//            py::overload_cast<std::vector<std::pair<std::string, std::string>>,
//                              a0::string_view,
//                              std::function<void(const a0::Packet&)>>(&a0::RpcClient::send))
//       .def("send",
//            py::overload_cast<a0::string_view, std::function<void(const a0::Packet&)>>(
//                &a0::RpcClient::send))
//       .def("cancel", &a0::RpcClient::cancel);

//   py::class_<a0::PrpcConnection>(m, "PrpcConnection")
//       .def_property_readonly("pkt", &a0::PrpcConnection::pkt)
//       .def("send", py::overload_cast<const a0::Packet&, bool>(&a0::PrpcConnection::send))
//       .def("send",
//            py::overload_cast<std::vector<std::pair<std::string, std::string>>,
//                              a0::string_view,
//                              bool>(&a0::PrpcConnection::send))
//       .def("send", py::overload_cast<a0::string_view, bool>(&a0::PrpcConnection::send));

//   py::class_<a0::PrpcServer, nogil_holder<a0::PrpcServer>>(m, "PrpcServer")
//       .def(py::init<a0::Arena,
//                     std::function<void(a0::PrpcConnection)>,
//                     std::function<void(a0::string_view)>>())
//       .def(py::init<a0::string_view,
//                     std::function<void(a0::PrpcConnection)>,
//                     std::function<void(a0::string_view)>>())
//       .def("async_close", &a0::PrpcServer::async_close);

//   py::class_<a0::PrpcClient, nogil_holder<a0::PrpcClient>>(m, "PrpcClient")
//       .def(py::init<a0::Arena>())
//       .def(py::init<a0::string_view>())
//       .def("async_close", &a0::PrpcClient::async_close)
//       .def("connect",
//            py::overload_cast<const a0::Packet&,
//                              std::function<void(const a0::Packet&, bool)>>(
//                &a0::PrpcClient::connect))
//       .def("connect",
//            py::overload_cast<std::vector<std::pair<std::string, std::string>>,
//                              a0::string_view,
//                              std::function<void(const a0::Packet&, bool)>>(
//                &a0::PrpcClient::connect))
//       .def("connect",
//            py::overload_cast<a0::string_view,
//                              std::function<void(const a0::Packet&, bool)>>(
//                &a0::PrpcClient::connect))
//       .def("cancel", &a0::PrpcClient::cancel);

}
