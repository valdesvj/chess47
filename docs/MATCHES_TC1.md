# CHESS47 matches, clock 3+2

CHESS47 (level 2, its book) in the C47 simulator against a python-chess player (2 plies, material, random among
equals), `python3 tools/match47.py 10 1 --tc 1`. Every move of the C47 checked legal, the board checked after every
move, the end of each game checked against the rules (python-chess). Over 120 plies: material.

The clock 3+2 (`--tc 1`), the simulator's time (0.17 ms a step): the C47's budget a move (LBL :TBUD:), level 1 for the move below 15 s.

**Score of the C47: 8 / 10**, 0 game(s) with a problem.

```
 1  C47 white  1-0     adjudicated at 86 plies (material +46)     1.0   86 plies  all moves legal, the end right
 2  C47 black  0-1     checkmate                                  1.0   48 plies  all moves legal, the end right
 3  C47 white  1-0     adjudicated at 88 plies (material +54)     1.0   88 plies  all moves legal, the end right
 4  C47 black  0-1     checkmate                                  1.0   74 plies  all moves legal, the end right
 5  C47 white  0-1     checkmate                                  0.0   28 plies  all moves legal, the end right
 6  C47 black  0-1     adjudicated at 63 plies (material -46)     1.0   63 plies  all moves legal, the end right
 7  C47 white  1/2-1/2 stalemate                                  0.5   65 plies  all moves legal, the end right
 8  C47 black  0-1     adjudicated at 61 plies (material -33)     1.0   61 plies  all moves legal, the end right
 9  C47 white  1-0     adjudicated at 80 plies (material +39)     1.0   80 plies  all moves legal, the end right
10  C47 black  1/2-1/2 stalemate                                  0.5   58 plies  all moves legal, the end right
```

## Game 1: C47 white, 1-0 (adjudicated at 86 plies (material +46))

1. e4 h6 2. d4 a5 3. Bxh6 Nc6 4. Bxg7 Ra7 5. Bxh8 Bh6 6. Be5 d6 7. Bxd6 a4 8. Bxe7 Bg7 9. Bxd8 Ra8 10. Bxc7 Ne5 11. Bxe5 Kd7 12. Bxg7 Rb8 13. Nd2 b5 14. Bxb5+ Kd8 15. Bxa4 Ra8 16. Ne2 Ra7 17. b4 f6 18. Bxf6+ Kc7 19. c4 Rb7 20. f4 Bf5 21. exf5 Kb8 22. g4 Re7 23. Bxe7 Nh6 24. h4 Kc7 25. Ne4 Kc8 26. O-O Kb8 27. a3 Kc8 28. b5 Nf7 29. c5 Ng5 30. fxg5 Kb8 31. d5 Kb7 32. Nd4 Kb8 33. h5 Kb7 34. b6 Kc8 35. c6 Kb8 36. f6 Ka8 37. g6 Kb8 38. g5 Kc8 39. h6 Kb8 40. b7 Kc7 41. b8=Q+ Kxb8 42. c7+ Ka7 43. c8=Q Kb6

## Game 2: C47 black, 0-1 (checkmate)

1. Nf3 d5 2. Nh4 e5 3. Nf3 Nc6 4. c3 Nf6 5. Qa4 a5 6. d3 b5 7. Bh6 bxa4 8. Nfd2 gxh6 9. b4 axb4 10. Na3 bxa3 11. f4 exf4 12. Nc4 dxc4 13. h3 cxd3 14. c4 dxe2 15. Kf2 exf1=Q+ 16. Rhxf1 Bxh3 17. Rac1 Bxg2 18. c5 Bxf1 19. Rb1 Bxc5+ 20. Ke1 Nd4 21. Rb3 axb3 22. Kd2 bxa2 23. Kc1 a1=Q+ 24. Kd2 Ne4#

## Game 3: C47 white, 1-0 (adjudicated at 88 plies (material +54))

1. e4 e6 2. d4 d6 3. Nd2 f6 4. Ne2 Ke7 5. a4 g6 6. b4 d5 7. exd5 c6 8. dxe6 c5 9. bxc5 g5 10. c4 Bh6 11. f4 g4 12. h4 Qf8 13. Ne4 g3 14. N2xg3 Ke8 15. Nxf6+ Kd8 16. Nxg8 Qf5 17. Nxf5 b5 18. Ngxh6 Ba6 19. axb5 Bc8 20. Rxa7 Na6 21. Rxa8 Kc7 22. Rxc8+ Kb7 23. Rxh8 Ka7 24. bxa6 Kxa6 25. Rxh7 Ka5 26. g4 Kb4 27. Be3 Ka3 28. Bd3 Kb4 29. O-O Ka3 30. d5 Kb4 31. g5 Ka5 32. Ng4 Kb4 33. Ne5 Kc3 34. h5 Kb4 35. c6 Kc3 36. c5 Kb2 37. g6 Ka2 38. h6 Kb2 39. c7 Ka2 40. c8=Q Kb2 41. c6 Ka3 42. c7 Ka2 43. e7 Kb2 44. e8=Q Kc3

## Game 4: C47 black, 0-1 (checkmate)

1. e3 d5 2. Qh5 e5 3. Qxf7+ Kxf7 4. d4 exd4 5. Nc3 dxc3 6. f3 cxb2 7. Bc4 bxa1=Q 8. Bd3 Qxc1+ 9. Kf2 Qxg1+ 10. Ke2 Qxh1 11. c3 Qxg2+ 12. Kd1 Qxf3+ 13. Kd2 Qxe3+ 14. Kc2 Qxd3+ 15. Kb2 Qxc3+ 16. Kxc3 Nc6 17. Kd2 Nf6 18. Kd3 Kg8 19. Kc2 a5 20. Kd2 b5 21. Ke3 g5 22. Kd2 h5 23. Kc2 Nd4+ 24. Kc3 c5 25. Kd2 Ne4+ 26. Ke1 Be6 27. h3 Bxh3 28. a4 bxa4 29. Kd1 Bf5 30. Ke1 Bd6 31. Kd1 a3 32. Kc1 a2 33. Kb2 a1=Q+ 34. Kxa1 a4 35. Kb2 a3+ 36. Ka1 a2 37. Kb2 a1=Q#

## Game 5: C47 white, 0-1 (checkmate)

1. d4 a5 2. e4 f6 3. Nd2 b6 4. Ne2 c5 5. dxc5 h5 6. cxb6 Rh7 7. a4 f5 8. exf5 Na6 9. b4 Nf6 10. bxa5 Rh8 11. c4 Kf7 12. f4 Ne8 13. g4 Nb4 14. gxh5 Nd3#

## Game 6: C47 black, 0-1 (adjudicated at 63 plies (material -46))

1. b4 d5 2. Ba3 e5 3. f4 Bxb4 4. h4 Bxa3 5. f5 Bxf5 6. Rh2 Qxh4+ 7. g3 Qxh2 8. Bg2 Qxg2 9. d4 Qxg1+ 10. Kd2 Qxd1+ 11. Ke3 Qxb1 12. Kd2 Qxa1 13. Ke3 Qxd4+ 14. Kf3 Bxc2 15. e4 Bxe4+ 16. Kg4 Nc6 17. Kh3 Nf6 18. g4 Nxg4 19. Kh4 a5 20. Kg5 b5 21. Kh4 f5 22. Kh5 g5 23. Kxg5 h5 24. Kh4 Bc5 25. Kg5 O-O 26. a3 Bxa3 27. Kh4 Bc5 28. Kh3 a4 29. Kg3 a3 30. Kh4 a2 31. Kg5 a1=Q 32. Kh4

## Game 7: C47 white, 1/2-1/2 (stalemate)

1. e4 b6 2. d4 Nc6 3. Nd2 e6 4. Ne2 Be7 5. a4 Kf8 6. b4 a5 7. bxa5 Na7 8. axb6 Qe8 9. bxa7 Bh4 10. c4 Bxf2+ 11. Kxf2 g5 12. Kg1 Qe7 13. g4 Nf6 14. h4 Ke8 15. hxg5 Ng8 16. Rxh7 Qa3 17. Rxa3 Nf6 18. Rxh8+ Ke7 19. Rxc8 Kd6 20. Rxa8 e5 21. gxf6 c5 22. dxe5+ Kc7 23. Nd4 Kb7 24. Bd3 Kb6 25. a5+ Ka6 26. g5 d5 27. cxd5+ Kb7 28. a6+ Kb6 29. g6 Kc7 30. gxf7 Kd7 31. f8=Q Kc7 32. Qxc5+ Kd7 33. f7

## Game 8: C47 black, 0-1 (adjudicated at 61 plies (material -33))

1. e3 d5 2. Qf3 e5 3. Qxf7+ Kxf7 4. Bb5 Nc6 5. Nh3 Bxh3 6. f4 exf4 7. Bc4 dxc4 8. Kf2 fxe3+ 9. Kf3 exd2 10. Rf1 dxc1=Q 11. g4 Qxf1+ 12. Ke4 Qxb1 13. a3 Qxa1 14. Kf5 Bxg4+ 15. Kf4 Qxa3 16. b3 cxb3 17. h4 Qxh4 18. c4 Nf6 19. Ke3 Kg8 20. c5 Bxc5+ 21. Kd3 a5 22. Kc3 b5 23. Kd3 g5 24. Kd2 h5 25. Kd3 Nd4 26. Ke3 Ne4 27. Kd3 b2+ 28. Kxe4 b1=Q+ 29. Kd5 Qe4+ 30. Kxe4 Qd3+ 31. Kxd3

## Game 9: C47 white, 1-0 (adjudicated at 80 plies (material +39))

1. e4 f5 2. exf5 a6 3. Bxa6 d6 4. Bxb7 Qd7 5. Bxa8 Ba6 6. d4 c6 7. Bxc6 Nh6 8. Bxd7+ Kf7 9. Bxh6 Be2 10. Nxe2 g5 11. Bxf8 h5 12. Bxe7 Rf8 13. Bxf8 Kg8 14. Bxd6 Kh8 15. Bxb8 h4 16. Nd2 Kh7 17. Be5 h3 18. gxh3 g4 19. hxg4 Kh6 20. a4 Kh7 21. b4 Kg8 22. c4 Kf8 23. f4 Kg8 24. h4 Kf8 25. Ne4 Kg8 26. O-O Kf7 27. a5 Ke7 28. b5 Kf8 29. c5 Ke7 30. d5 Kd8 31. Nd4 Ke7 32. g5 Kd8 33. h5 Ke7 34. a6 Kf7 35. b6 Kg8 36. c6 Kf7 37. f6 Kf8 38. f5 Kg8 39. g6 Kf8 40. h6 Kg8

## Game 10: C47 black, 1/2-1/2 (stalemate)

1. b4 d5 2. Nf3 e5 3. d3 Bxb4+ 4. Nc3 Bxc3+ 5. Bd2 Bxa1 6. Ng5 Qxg5 7. Rg1 Qxd2+ 8. Qxd2 Bd4 9. c3 Bxc3 10. g3 Bxd2+ 11. Kd1 Nc6 12. Rg2 Nf6 13. h4 a5 14. e3 Bxe3 15. Ke1 Bxf2+ 16. Ke2 Bxg3 17. Kf3 Bxh4 18. Rb2 b5 19. Kg2 g5 20. Rf2 Bxf2 21. a4 bxa4 22. Kh2 h5 23. Be2 Nd4 24. Bg4 hxg4+ 25. Kg2 c5 26. Kf1 Ne4 27. Kg2 f5 28. Kf1 Rh2 29. dxe4 fxe4

