//Matthew Ferreira
//Feb 20, 2018
//Port Scanner

#include <fcntl.h>
#include <cerrno>
#include <cstdlib>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <stdio.h>
#include <iostream>
#include <cstring>
#include <netinet/in.h>
#include <netdb.h>
#include <netinet/tcp.h>

int main (int argc, char **argv)
{
    int port1 = 1;
    int port2 = 1024;

    struct addrinfo hints;
    struct addrinfo *result, *rp;
    int sfd, s;

    opterr = 1;

    if(argc > 2) {
        if(getopt(argc, argv, "p:") != -1){
            char *loc = strchr(optarg,':');
            if(loc == NULL){
                std::cerr << "Invalid option: " << optarg << std::endl;
                exit(EXIT_FAILURE);
            }
            port1 = std::atoi(strtok(optarg, ":"));
            port2 = std::atoi(strtok(NULL, ":"));
        }
    else{
           std::cerr << optopt;
        }
    }
    else {
    optind = 1;
    }


for(int p = port1; p <= port2; p++){
        memset(&hints, 0, sizeof(struct addrinfo));
        hints.ai_family = AF_INET;
        hints.ai_socktype = SOCK_STREAM;
        hints.ai_flags = 0;
        hints.ai_protocol = 0;

        std::string p1 = std::to_string(p);
        s = getaddrinfo(argv[optind], p1.c_str(), &hints, &result);

        if (s != 0) {
            fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(s));
            exit(EXIT_FAILURE);
        }

    for (rp = result; rp != NULL; rp = rp->ai_next) {
            sfd = socket(rp->ai_family, rp->ai_socktype,
                     rp->ai_protocol);
            if (sfd == -1){
                continue;
            }

            int syncnt = 1;
            int syncnt_sz = sizeof(syncnt);
            setsockopt(sfd, IPPROTO_TCP, TCP_SYNCNT, &syncnt, syncnt_sz);

            if(connect(sfd, rp->ai_addr, rp->ai_addrlen) != -1)
                break;

            close(sfd);
        }

    if (rp != NULL) {
            std::cout << p << std::endl;
        }
    }


