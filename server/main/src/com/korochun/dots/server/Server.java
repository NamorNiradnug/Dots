package com.korochun.dots.server;

import java.io.IOException;
import java.net.ServerSocket;

public class Server {

    public static void main(String[] args) throws IOException {
        new Server().start();
    }

    private void start() throws IOException {
        ServerSocket server = new ServerSocket(5722);
        while (true) {
            Player player = new Player(server.accept());
            System.out.println("Incoming connection!");
        }
    }
}
