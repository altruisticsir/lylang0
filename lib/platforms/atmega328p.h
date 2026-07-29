#ifndef CONTROL
#define CONTROL

#define F_CPU 16000000

#include <avr/io.h>
#include <util/delay.h>

#define OFF 0
#define ON 1
#define TOGGLE 2

#define IN 0
#define OUT 1

namespace Digital
{
    template <int PortNumber>
    struct Port;

    template <>
    struct Port<0>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 0; }
    };
    template <>
    struct Port<1>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 1; }
    };
    template <>
    struct Port<2>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 2; }
    };
    template <>
    struct Port<3>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 3; }
    };
    template <>
    struct Port<4>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 4; }
    };
    template <>
    struct Port<5>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 5; }
    };
    template <>
    struct Port<6>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 6; }
    };
    template <>
    struct Port<7>
    {
        static volatile uint8_t &port() { return PORTD; }
        static volatile uint8_t &ddr() { return DDRD; }
        static volatile int pin() { return 7; }
    };
    template <>
    struct Port<8>
    {
        static volatile uint8_t &port() { return PORTB; }
        static volatile uint8_t &ddr() { return DDRB; }
        static volatile int pin() { return 0; }
    };
    template <>
    struct Port<9>
    {
        static volatile uint8_t &port() { return PORTB; }
        static volatile uint8_t &ddr() { return DDRB; }
        static volatile int pin() { return 1; }
    };
    template <>
    struct Port<10>
    {
        static volatile uint8_t &port() { return PORTB; }
        static volatile uint8_t &ddr() { return DDRB; }
        static volatile int pin() { return 2; }
    };
    template <>
    struct Port<11>
    {
        static volatile uint8_t &port() { return PORTB; }
        static volatile uint8_t &ddr() { return DDRB; }
        static volatile int pin() { return 3; }
    };
    template <>
    struct Port<12>
    {
        static volatile uint8_t &port() { return PORTB; }
        static volatile uint8_t &ddr() { return DDRB; }
        static volatile int pin() { return 4; }
    };
    template <>
    struct Port<13>
    {
        static volatile uint8_t &port() { return PORTB; }
        static volatile uint8_t &ddr() { return DDRB; }
        static volatile int pin() { return 5; }
    };

    template <int PortNumber>
    inline void flip(int state)
    {
        switch (state)
        {
        case OFF:
            Port<PortNumber>::port() &= ~(1 << Port<PortNumber>::pin());
            break;

        case ON:
            Port<PortNumber>::port() |= (1 << Port<PortNumber>::pin());
            break;

        case TOGGLE:
            Port<PortNumber>::port() ^= (1 << Port<PortNumber>::pin());
            break;

        default:
            break;
        }
    }

    template <int PortNumber>
    inline void set(int state)
    {
        switch (state)
        {
        case IN:
            Port<PortNumber>::ddr() &= ~(1 << Port<PortNumber>::pin());
            break;

        case OUT:
            Port<PortNumber>::ddr() |= (1 << Port<PortNumber>::pin());
            break;

        default:
            break;
        }
    }
}
namespace Delay
{
    inline void ms(int ms)
    {
        _delay_ms(ms);
    }
    inline void us(int us)
    {
        _delay_us(us);
    }
}

#endif