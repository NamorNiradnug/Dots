package com.korochun.dots.server.test;

import java.io.IOException;
import java.net.Socket;

public class ServerTest {
    public static void main(String[] args) throws IOException {
        new Socket("localhost", 5722).getOutputStream().write(new byte[] { 1, 10, 8, 'k', 'o', 'r', 'o', 'c', 'h', 'u', 'n', 0 });
    }
}
