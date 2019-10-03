package com.korochun.dots.server;

import org.jetbrains.annotations.Contract;
import org.jetbrains.annotations.NotNull;

import java.io.IOException;
import java.io.InputStream;
import java.net.Socket;

public class Player implements Runnable {
    public static final byte FIND = 0x00;
    public static final byte FOUND = 0x01;
    public static final byte PLAY = 0x02;
    public static final byte TIE = 0x04;
    public static final byte SURRENDER = 0x05;
    public static final byte END = 0x07;
    public static final byte CONFIRM = 0x7F;
    public static final byte ERROR = (byte) 0xFF;

    private Game game;
    private Socket socket;
    private String name;

    private volatile boolean started = false, myTurn, ended = false;

    @Contract(pure = true)
    public Player(Socket socket) {
        this.socket = socket;
        new Thread(this).start();
    }

    public void run() {
        try {
            InputStream input = socket.getInputStream();
            while (!ended) {
                byte id = (byte) input.read();
                switch (id) {
                    case FIND:

                }
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    public void found(@NotNull Player player, boolean myTurn) {
        this.myTurn = myTurn;
        this.send(FOUND, player.name, (byte) (myTurn ? 1 : 0));
    }

    private void send(byte id, Object... payload) {
        socket.getOutputStream().write();
    }

    public void end() {
        ended = true;
        while (!started) {

        }
    }

    public void setGame(Game game) {
        this.game = game;
    }
}
