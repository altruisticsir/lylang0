proc wow(a) {
    return a
}
proc main() {
    digital.set(8, OUT)
    digital.set(9, OUT)

    digital.flip(8, TOGGLE)

    wow(10.0)

    while (true) {
        digital.flip(8, TOGGLE)
        digital.flip(9, TOGGLE)
        delay.ms(555)
    }
}