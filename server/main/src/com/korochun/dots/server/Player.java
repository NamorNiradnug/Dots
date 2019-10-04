package com.korochun.dots.server;

import org.jetbrains.annotations.Contract;

import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;
import java.util.Arrays;

public class Player extends Thread {
    private Socket socket;

    @Contract(pure = true)
    public Player(Socket socket) {
        this.socket = socket;
        this.start();
    }

    @Override
    public void run() {
        try {
            while (true) {
                this.receive();
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private synchronized void receive() throws IOException {
        InputStream in = this.socket.getInputStream();
        int packetType = -1, length = -1, i = -1, last = -1;
        byte[] payload = null;
        while (last != 0) {
            last = in.read();
            if (last != -1) {
                if (packetType == -1) {
                    packetType = last;
                } else if (i == -1) {
                    length = last;
                    payload = new byte[length];
                    i = 0;
                } else {
                    if (i < length && last != 0) {
                        payload[i] = (byte) last;
                    }
                    i++;
                }
            }
        }
        if (i > length) {
            socket.close();
            throw new IOException("Payload longer than expected! Expected " + length + " bytes, got " + (i + 1) + " bytes");
        }
        System.out.println("Packet type: " + packetType + "\nPayload: " + Arrays.toString(payload));
    }
}
