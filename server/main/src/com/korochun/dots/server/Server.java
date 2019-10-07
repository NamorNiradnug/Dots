package com.korochun.dots.server;

import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

import java.io.IOException;
import java.net.ServerSocket;
import java.net.Socket;

public class Server {
    static final Logger LOGGER = LogManager.getLogger();

    public static void main(String[] args) throws IOException {
        LOGGER.info("Starting...");
        new Server().start();
    }

    private void start() throws IOException {
        ServerSocket server = new ServerSocket(5722);
        LOGGER.info("Ready!");
        //noinspection InfiniteLoopStatement
        while (true) {
            Socket socket = server.accept();
            LOGGER.info("Incoming connection from " + socket.getInetAddress());
            Connection connection = new Connection(socket);
        }
    }
}
