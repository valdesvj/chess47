# Chess 47 against itself: the rules check

`python3 tools/selfplay47.py 1 0,1`: CHESS47 in the C47 simulator plays itself (key 9), python-chess checks every move, the board after it, the end of the game and the clock (5 minutes + 10 s a move).

| level | seed | result | plies | clock W | clock B | check |
|---|---|---|---|---|---|---|
| 0 | 1 | CHECKMATE | 91 | 10:36 | 10:33 | rules kept |
| 1 | 101 | STALEMATE | 93 | 8:18 | 9:37 | rules kept |

## The games

**Level 0, seed 1: CHECKMATE**

1. Nf3 Nh6 2. b3 a5 3. g4 Ra7 4. a3 Ra6 5. e3 c6 6. Rg1 b5 7. Bd3 b4 8. Ng5 Nf5 9. c3 Ng3 10. Bc2 Qc7 11. cxb4 Kd8 12. Nh3 f6 13. Rf1 e5 14. d4 Bxb4+ 15. axb4 Qd6 16. fxg3 Qxb4+ 17. Nd2 Ra7 18. Rf5 Qb5 19. Ng1 g6 20. Ra4 c5 21. Bb1 d5 22. dxc5 e4 23. Qc2 Kd7 24. Nh3 Kc6 25. Rxe4 Kc7 26. Qd1 Rd8 27. Ra4 Re8 28. Ba2 Rg8 29. Rxd5 Kc6 30. Bb1 Qb7 31. Ng1 Re8 32. Ndf3 Qb4+ 33. Kf1 Qxb3 34. Ba2 Nd7 35. Rb4 Re4 36. Ke2 Rxb4 37. Qd3 Nb6 38. Qb5+ Kb7 39. Rd3 Ka8 40. Qxa5 Qg8 41. Rd2 Rb1 42. Rd8 Qf7 43. Nh3 h6 44. Ba3 f5 45. Qxb6 Rg1 46. Rxc8#

**Level 1, seed 101: STALEMATE**

1. d4 d5 2. c4 c6 3. Nf3 Nf6 4. Nc3 dxc4 5. a4 Bf5 6. e4 Nxe4 7. Nxe4 Bxe4 8. Bxc4 Bxf3 9. gxf3 Qxd4 10. Qxd4 e5 11. Qxe5+ Be7 12. Qxe7+ Kxe7 13. Bxf7 Kxf7 14. b4 Kg8 15. h4 Nd7 16. Be3 a5 17. bxa5 Rxa5 18. O-O Rxa4 19. Rxa4 b5 20. Ra7 g5 21. Rxd7 gxh4 22. Rxh7 Rxh7 23. f4 h3 24. f3 h2+ 25. Kh1 b4 26. f5 b3 27. f4 b2 28. f6 b1=Q 29. Rxb1 c5 30. Bxc5 Kh8 31. Rb7 Rxb7 32. Kxh2 Rb2+ 33. Kh1 Ra2 34. f5 Rb2 35. f7 Ra2 36. f8=Q+ Kh7 37. f6 Rb2 38. f7 Ra2 39. Qd6 Kh8 40. f8=Q+ Kh7 41. Qf5+ Kh8 42. Bd4+ Kg8 43. Qe4 Rb2 44. Bxb2 Kf7 45. Bd4 Kg8 46. Qde5 Kf8 47. Q4d5

