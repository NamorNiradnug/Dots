package com.korochun.dots.server;

import java.io.IOException;
import java.net.ServerSocket;
import java.util.ArrayList;

public class Server implements Runnable {
    private ArrayList<Game> games = new ArrayList<>();

    public static void main(String[] args) throws IOException {
        new Server().start();
    }

    private void start() throws IOException {
        Runtime.getRuntime().addShutdownHook(new Thread(this));
        ServerSocket socket = new ServerSocket(57922);
        //noinspection InfiniteLoopStatement
        while (true) {
            Player player = new Player(socket.accept());
            if (!games.isEmpty()) {
                Game game = games.get(games.size() - 1);
                if (!game.isFull()) {
                    game.addPlayer(player);
                    continue;
                }
            }
            games.add(new Game(player));
        }
    }

    public void run() {
        for (Game game : games)
            game.stop();
    }
}
