package com.korochun.dots.server;

import org.jetbrains.annotations.Contract;

public class Game {
    private Player player1, player2;
    private boolean turn;

    @Contract(pure = true)
    public Game(Player player) {
        player1 = player;
    }

    public boolean isFull() {
        return player2 != null;
    }

    public void addPlayer(Player player) {
        if (isFull())
            throw new IllegalStateException("Game already full");
        player2 = player;
        turn = Math.random() * 2 >= 1;
        player1.found(player2, turn);
        player2.found(player1, !turn);
    }

    public void stop() {
        player1.end();
        player2.end();
    }
}
