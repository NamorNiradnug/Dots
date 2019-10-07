package com.korochun.dots.server;

import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NotNull;

import java.io.*;
import java.net.Socket;

public class Connection extends Thread {
    public static final byte FIND = 0x00;
    public static final byte PLAY = 0x01;

    public static final byte TIE = 0x04;
    public static final byte SURRENDER = 0x05;
    public static final byte END = 0x07;

    public static final byte CONFIRM = 0x7F;
    public static final byte ERROR = (byte) 0xFF;

    private final DataInputStream in;
    private final DataOutputStream out;
    private byte state = 0;

    @Contract(pure = true)
    public Connection(@NotNull Socket socket) throws IOException {
        this.in = new DataInputStream(socket.getInputStream());
        this.out = new DataOutputStream(socket.getOutputStream());
        this.start();
    }

    @Override
    public void run() {
        try {
            try {
                while (state != 3) {
                    switch (in.readByte()) {
                        case FIND:
                            in.readInt();
                            if (state == 0) {
                                confirm(true);
                                state++;
                            } else {
                                confirm(false);
                            }
                            break;
                        case PLAY:
                            // TODO: Implement Game
                        case TIE:
                            // TODO: Implement Game
                        case SURRENDER:
                            // TODO: Implement Game
                        case END:
                            confirm(false);
                        case CONFIRM:
                            // TODO: Implement CONFIRM
                        case ERROR:
                            // TODO: Implement Game
                    }
                }
            } catch (Exception e) {
                Server.LOGGER.error("An unexpected error occurred, while communicating with a player!", e);
                error(e.getMessage());
            }
            state = 3;
        } catch (IOException ignored) {
        }
    }

    private void confirm(boolean b) throws IOException {
        out.writeByte(CONFIRM);
        out.writeInt(1);
        out.writeBoolean(b);
    }

    private void error(String message) throws IOException {
        out.writeByte(ERROR);
        out.writeInt(message.length() + 1);
        out.writeByte(message.length());
        for (char c : message.toCharArray()) {
            out.writeChar(c);
        }
    }
}
