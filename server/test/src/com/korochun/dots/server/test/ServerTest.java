package com.korochun.dots.server.test;

import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.Socket;

public class ServerTest {
    public static void main(String[] args) throws IOException {
        Socket socket = new Socket("localhost", 5722);
        InputStream in = socket.getInputStream();
        OutputStream out = socket.getOutputStream();

        new Packet((byte) 0).writeString("korochun").writeBoolean(false).send(out);
        System.out.println(Packet.receive(in));
        new Packet((byte) 0).writeString("korochun").writeBoolean(false).send(out);
        System.out.println(Packet.receive(in));
    }
}
