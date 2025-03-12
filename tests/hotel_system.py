from datetime import date, timedelta


class Room:
    def __init__(self, number, room_type, price_per_day, capacity):
        self.number = number
        self.room_type = room_type
        self.price_per_day = price_per_day
        self.capacity = capacity
        self.bookings = []  # List of Booking objects

    def is_available_for(self, start_date, end_date):
        # Check if the room is available for the date range [start_date, end_date)
        for booking in self.bookings:
            # If the booking overlaps with the requested range, return False
            if not (end_date <= booking.start_date or start_date >= booking.end_date):
                return False
        return True

    def add_booking(self, booking):
        self.bookings.append(booking)


class Booking:
    def __init__(self, booking_id, room, guest_name, start_date, end_date):
        self.booking_id = booking_id
        self.room = room
        self.guest_name = guest_name
        self.start_date = start_date
        self.end_date = end_date
        self.total_price = self.calculate_total_price()

    def calculate_total_price(self):
        num_days = (self.end_date - self.start_date).days
        price = num_days * self.room.price_per_day
        if num_days > 5:
            price *= 0.9  # Apply 10% discount for stays longer than 5 days
        return price

    def update_dates(self, new_start_date, new_end_date):
        if new_start_date >= new_end_date:
            raise Exception("Invalid date range")
        self.start_date = new_start_date
        self.end_date = new_end_date
        self.total_price = self.calculate_total_price()


class Hotel:
    def __init__(self, name, rooms):
        self.name = name
        self.rooms = rooms
        self.bookings = {}  # Mapping booking_id to Booking objects

    def generate_booking_id(self):
        return len(self.bookings) + 1

    def book_room(self, room_number, guest_name, start_date, end_date):
        room = next((r for r in self.rooms if r.number == room_number), None)
        if room is None:
            raise Exception("Room not found")
        if start_date >= end_date:
            raise Exception("Invalid date range")
        if not room.is_available_for(start_date, end_date):
            raise Exception("Room not available for the selected dates")
        booking_id = self.generate_booking_id()
        booking = Booking(booking_id, room, guest_name, start_date, end_date)
        room.add_booking(booking)
        self.bookings[booking_id] = booking
        return booking_id

    def cancel_booking(self, booking_id):
        if booking_id not in self.bookings:
            raise Exception("Booking not found")
        booking = self.bookings.pop(booking_id)
        booking.room.bookings.remove(booking)

    def get_available_rooms(self, start_date, end_date):
        return [room.number for room in self.rooms if room.is_available_for(start_date, end_date)]

    def get_total_income(self):
        return sum(booking.total_price for booking in self.bookings.values())

    def get_booking_info(self, booking_id):
        if booking_id not in self.bookings:
            raise Exception("Booking not found")
        b = self.bookings[booking_id]
        return f"Booking {b.booking_id} for room {b.room.number} by {b.guest_name} from {b.start_date} to {b.end_date} for {b.total_price:.2f}"

    def report(self):
        # Report: number of bookings per room
        return {room.number: len(room.bookings) for room in self.rooms}

    def update_booking(self, booking_id, new_start_date, new_end_date):
        if booking_id not in self.bookings:
            raise Exception("Booking not found")
        booking = self.bookings[booking_id]
        room = booking.room
        # Temporarily remove the booking from the room's bookings list
        room.bookings.remove(booking)
        if not room.is_available_for(new_start_date, new_end_date):
            room.bookings.append(booking)
            raise Exception("Room not available for the new selected dates")
        # Update the booking's dates
        booking.update_dates(new_start_date, new_end_date)
        room.bookings.append(booking)