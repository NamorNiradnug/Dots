package com.korochun.dots.server.test;

import org.jetbrains.annotations.NotNull;

import java.io.*;
import java.net.Socket;

public class ServerTest {
    public static final byte FIND = 0x00;
    public static final byte PLAY = 0x01;

    public static final byte TIE = 0x04;
    public static final byte SURRENDER = 0x05;
    public static final byte END = 0x07;

    public static final byte CONFIRM = 0x7F;
    public static final byte ERROR = (byte) 0xFF;

    private final DataInputStream in;
    private final DataOutputStream out;

    private ServerTest(@NotNull Socket socket) throws IOException {
        this.in = new DataInputStream(socket.getInputStream());
        this.out = new DataOutputStream(socket.getOutputStream());
        this.start();
    }

    public static void main(String[] args) throws IOException {
        new ServerTest(new Socket("localhost", 5722));
    }

    private void start() throws IOException {
        find("korochun", false);
        find("korochun", false);
    }

    private void writeString(@NotNull String string) throws IOException {
        out.writeByte(string.length());
        for (char c : string.toCharArray()) {
            out.writeChar(c);
        }
    }

    private void find(@NotNull String nickname, boolean myTurn) throws IOException {
        out.writeByte(FIND);
        out.writeInt(nickname.length() + 2);
        writeString(nickname);
        out.writeBoolean(myTurn);
    }
}
