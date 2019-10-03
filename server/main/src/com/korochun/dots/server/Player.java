package com.korochun.dots.server;

import org.jetbrains.annotations.Contract;

import java.net.Socket;

public class Player implements Runnable {
    private Socket socket;
    private String name;
    private volatile boolean started = false, myTurn, ended = false;

    @Contract(pure = true)
    public Player(Socket socket) {
        this.socket = socket;
        new Thread(this).start();
    }

    public void run() {
        while (!ended) {

        }
    }

    public void found(Player player, boolean myTurn) {

    }

    public void end() {

    }
}
