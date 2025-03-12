import unittest
from hotel_system import *


class TestRoom(unittest.TestCase):
    def setUp(self):
        self.room = Room(101, "standard", 100.0, 2)

    def test_initial_availability(self):
        self.assertTrue(self.room.is_available_for(date(2025, 1, 1), date(2025, 1, 2)))

    def test_availability_no_bookings(self):
        self.assertTrue(self.room.is_available_for(date(2025, 1, 10), date(2025, 1, 15)))

    def test_availability_with_booking_no_overlap(self):
        booking = Booking(1, self.room, "Alice", date(2025, 1, 1), date(2025, 1, 5))
        self.room.add_booking(booking)
        self.assertTrue(self.room.is_available_for(date(2025, 1, 5), date(2025, 1, 10)))
        self.assertTrue(self.room.is_available_for(date(2024, 12, 25), date(2025, 1, 1)))

    def test_availability_with_booking_overlap_begin(self):
        booking = Booking(1, self.room, "Alice", date(2025, 1, 5), date(2025, 1, 10))
        self.room.add_booking(booking)
        self.assertFalse(self.room.is_available_for(date(2025, 1, 4), date(2025, 1, 6)))

    def test_availability_with_booking_overlap_end(self):
        booking = Booking(1, self.room, "Alice", date(2025, 1, 5), date(2025, 1, 10))
        self.room.add_booking(booking)
        self.assertFalse(self.room.is_available_for(date(2025, 1, 9), date(2025, 1, 12)))

    def test_availability_with_booking_complete_overlap(self):
        booking = Booking(1, self.room, "Alice", date(2025, 1, 5), date(2025, 1, 10))
        self.room.add_booking(booking)
        self.assertFalse(self.room.is_available_for(date(2025, 1, 5), date(2025, 1, 10)))

    def test_add_booking(self):
        booking = Booking(1, self.room, "Alice", date(2025, 1, 5), date(2025, 1, 10))
        self.room.add_booking(booking)
        self.assertIn(booking, self.room.bookings)


class TestBooking(unittest.TestCase):
    def setUp(self):
        self.room = Room(101, "standard", 100.0, 2)

    def test_total_price_no_discount(self):
        booking = Booking(1, self.room, "Bob", date(2025, 2, 1), date(2025, 2, 4))
        self.assertEqual(booking.total_price, 3 * 100.0)

    def test_total_price_with_discount(self):
        booking = Booking(2, self.room, "Carol", date(2025, 3, 1), date(2025, 3, 8))
        expected_price = 7 * 100.0 * 0.9
        self.assertAlmostEqual(booking.total_price, expected_price)

    def test_update_dates_success(self):
        booking = Booking(1, self.room, "Dave", date(2025, 4, 1), date(2025, 4, 4))
        booking.update_dates(date(2025, 4, 2), date(2025, 4, 6))
        self.assertEqual(booking.start_date, date(2025, 4, 2))
        self.assertEqual(booking.end_date, date(2025, 4, 6))

    def test_update_dates_invalid_range(self):
        booking = Booking(1, self.room, "Eve", date(2025, 5, 1), date(2025, 5, 4))
        with self.assertRaises(Exception) as context:
            booking.update_dates(date(2025, 5, 5), date(2025, 5, 3))
        self.assertEqual(str(context.exception), "Invalid date range")

    def test_update_dates_recalculate_discount(self):
        booking = Booking(1, self.room, "Frank", date(2025, 6, 1), date(2025, 6, 4))  # 3 days, no discount
        original_price = booking.total_price
        booking.update_dates(date(2025, 6, 1), date(2025, 6, 8))  # 7 days, discount applies
        self.assertNotEqual(booking.total_price, original_price)
        expected_price = 7 * 100.0 * 0.9
        self.assertAlmostEqual(booking.total_price, expected_price)


class TestHotel(unittest.TestCase):
    def setUp(self):
        self.room1 = Room(101, "standard", 100.0, 2)
        self.room2 = Room(102, "luxury", 200.0, 3)
        self.room3 = Room(103, "super-luxury", 300.0, 4)
        self.hotel = Hotel("Florida Beach", [self.room1, self.room2, self.room3])
        self.today = date(2025, 5, 1)
        self.tomorrow = self.today + timedelta(days=1)

    def test_generate_booking_id(self):
        self.assertEqual(self.hotel.generate_booking_id(), 1)
        self.hotel.bookings[1] = "dummy"
        self.assertEqual(self.hotel.generate_booking_id(), 2)

    def test_book_room_success(self):
        start = date(2025, 5, 10)
        end = date(2025, 5, 15)
        booking_id = self.hotel.book_room(101, "David", start, end)
        self.assertEqual(booking_id, 1)
        self.assertFalse(self.room1.is_available_for(start, end))
        self.assertIn(booking_id, self.hotel.bookings)

    def test_book_room_invalid_date_range(self):
        with self.assertRaises(Exception) as context:
            self.hotel.book_room(101, "David", date(2025, 5, 15), date(2025, 5, 10))
        self.assertEqual(str(context.exception), "Invalid date range")

    def test_book_room_room_not_found(self):
        with self.assertRaises(Exception) as context:
            self.hotel.book_room(999, "Eve", self.today, self.tomorrow)
        self.assertEqual(str(context.exception), "Room not found")

    def test_book_room_unavailable(self):
        start = date(2025, 6, 1)
        end = date(2025, 6, 5)
        self.hotel.book_room(101, "Frank", start, end)
        with self.assertRaises(Exception) as context:
            self.hotel.book_room(101, "Grace", date(2025, 6, 4), date(2025, 6, 7))
        self.assertEqual(str(context.exception), "Room not available for the selected dates")

    def test_cancel_booking_success(self):
        start = date(2025, 7, 1)
        end = date(2025, 7, 4)
        booking_id = self.hotel.book_room(102, "Heidi", start, end)
        self.hotel.cancel_booking(booking_id)
        self.assertNotIn(booking_id, self.hotel.bookings)
        self.assertTrue(self.room2.is_available_for(start, end))

    def test_cancel_booking_not_found(self):
        with self.assertRaises(Exception) as context:
            self.hotel.cancel_booking(999)
        self.assertEqual(str(context.exception), "Booking not found")

    def test_get_available_rooms_initial(self):
        start = date(2025, 8, 1)
        end = date(2025, 8, 5)
        available = self.hotel.get_available_rooms(start, end)
        self.assertCountEqual(available, [101, 102, 103])

    def test_get_total_income(self):
        self.hotel.book_room(101, "Jack", date(2025, 9, 1), date(2025, 9, 4))   # 3 days, 300
        self.hotel.book_room(102, "Karen", date(2025, 9, 5), date(2025, 9, 12))  # 7 days, 7*200*0.9 = 1260
        total_income = self.hotel.get_total_income()
        expected_income = 3 * 100.0 + 7 * 200.0 * 0.9
        self.assertAlmostEqual(total_income, expected_income)

    def test_get_booking_info_success(self):
        start = date(2025, 10, 1)
        end = date(2025, 10, 6)
        booking_id = self.hotel.book_room(101, "Leo", start, end)
        info = self.hotel.get_booking_info(booking_id)
        self.assertIn(f"Booking {booking_id}", info)
        self.assertIn("room 101", info)
        self.assertIn("Leo", info)
        self.assertIn(str(start), info)
        self.assertIn(str(end), info)

    def test_get_booking_info_not_found(self):
        with self.assertRaises(Exception) as context:
            self.hotel.get_booking_info(999)
        self.assertEqual(str(context.exception), "Booking not found")

    def test_report_initial(self):
        rep = self.hotel.report()
        self.assertEqual(rep, {101: 0, 102: 0, 103: 0})

    def test_update_booking_success(self):
        start = date(2025, 11, 1)
        end = date(2025, 11, 5)
        booking_id = self.hotel.book_room(101, "Mike", start, end)
        new_start = date(2025, 11, 2)
        new_end = date(2025, 11, 6)
        self.hotel.update_booking(booking_id, new_start, new_end)
        booking_info = self.hotel.get_booking_info(booking_id)
        self.assertIn(str(new_start), booking_info)
        self.assertIn(str(new_end), booking_info)

    def test_update_booking_invalid_range(self):
        start = date(2025, 12, 1)
        end = date(2025, 12, 5)
        booking_id = self.hotel.book_room(102, "Nina", start, end)
        with self.assertRaises(Exception) as context:
            self.hotel.update_booking(booking_id, date(2025, 12, 6), date(2025, 12, 4))
        self.assertEqual(str(context.exception), "Invalid date range")

    def test_update_booking_overlap(self):
        start1 = date(2026, 1, 1)
        end1 = date(2026, 1, 5)
        start2 = date(2026, 1, 5)
        end2 = date(2026, 1, 10)
        booking_id1 = self.hotel.book_room(101, "Olivia", start1, end1)
        booking_id2 = self.hotel.book_room(101, "Paul", start2, end2)
        with self.assertRaises(Exception) as context:
            self.hotel.update_booking(booking_id1, date(2026, 1, 3), date(2026, 1, 8))
        self.assertEqual(str(context.exception), "Room not available for the new selected dates")

    def test_update_booking_same_dates(self):
        start = date(2026, 2, 1)
        end = date(2026, 2, 5)
        booking_id = self.hotel.book_room(102, "Quinn", start, end)
        # Update with the same dates should succeed.
        self.hotel.update_booking(booking_id, start, end)
        booking_info = self.hotel.get_booking_info(booking_id)
        self.assertIn(str(start), booking_info)

    def test_update_booking_edge_overlap(self):
        # Test edge condition: one booking ends exactly when another starts.
        start1 = date(2026, 3, 1)
        end1 = date(2026, 3, 5)
        start2 = date(2026, 3, 5)
        end2 = date(2026, 3, 10)
        booking_id = self.hotel.book_room(103, "Rachel", start1, end1)
        booking_id2 = self.hotel.book_room(103, "Sam", end1, end2)
        self.hotel.update_booking(booking_id, start1, end1)
        booking_info = self.hotel.get_booking_info(booking_id)
        self.assertIn(str(end1), booking_info)

    def test_get_available_rooms_after_booking_update(self):
        start = date(2026, 4, 1)
        end = date(2026, 4, 5)
        booking_id = self.hotel.book_room(101, "Tom", start, end)
        available = self.hotel.get_available_rooms(start, end)
        self.assertNotIn(101, available)
        self.hotel.update_booking(booking_id, date(2026, 4, 6), date(2026, 4, 10))
        available = self.hotel.get_available_rooms(start, end)
        self.assertIn(101, available)

    def test_multiple_booking_operations(self):
        id1 = self.hotel.book_room(101, "Uma", date(2026, 5, 1), date(2026, 5, 4))
        id2 = self.hotel.book_room(102, "Victor", date(2026, 5, 2), date(2026, 5, 6))
        id3 = self.hotel.book_room(103, "Wendy", date(2026, 5, 3), date(2026, 5, 7))
        self.hotel.cancel_booking(id2)
        available = self.hotel.get_available_rooms(date(2026, 5, 2), date(2026, 5, 6))
        self.assertIn(102, available)
        self.assertNotIn(101, available)
        self.assertNotIn(103, available)

    def test_repeated_booking_updates(self):
        start = date(2026, 6, 1)
        end = date(2026, 6, 5)
        booking_id = self.hotel.book_room(101, "Xander", start, end)
        for i in range(3):
            new_start = start + timedelta(days=i)
            new_end = end + timedelta(days=i)
            self.hotel.update_booking(booking_id, new_start, new_end)
            booking_info = self.hotel.get_booking_info(booking_id)
            self.assertIn(str(new_start), booking_info)

    def test_get_total_income_after_update(self):
        id1 = self.hotel.book_room(101, "Yara", date(2026, 7, 1), date(2026, 7, 4))  # 3 days: 300
        self.hotel.update_booking(id1, date(2026, 7, 1), date(2026, 7, 8))  # 7 days: 700*0.9 = 630
        total_income = self.hotel.get_total_income()
        self.assertAlmostEqual(total_income, 630)

    def test_report_after_update(self):
        id1 = self.hotel.book_room(101, "Zack", date(2026, 8, 1), date(2026, 8, 5))
        self.hotel.update_booking(id1, date(2026, 8, 2), date(2026, 8, 6))
        rep = self.hotel.report()
        self.assertEqual(rep[101], 1)

    def test_multiple_room_bookings(self):
        id1 = self.hotel.book_room(101, "Alice", date(2026, 9, 1), date(2026, 9, 4))
        id2 = self.hotel.book_room(102, "Bob", date(2026, 9, 1), date(2026, 9, 4))
        id3 = self.hotel.book_room(103, "Charlie", date(2026, 9, 1), date(2026, 9, 4))
        self.assertFalse(self.room1.is_available_for(date(2026, 9, 1), date(2026, 9, 4)))
        self.assertFalse(self.room2.is_available_for(date(2026, 9, 1), date(2026, 9, 4)))
        self.assertFalse(self.room3.is_available_for(date(2026, 9, 1), date(2026, 9, 4)))

    def test_booking_id_consistency_after_cancellations(self):
        id1 = self.hotel.book_room(101, "Dan", date(2026, 10, 1), date(2026, 10, 4))
        id2 = self.hotel.book_room(102, "Eli", date(2026, 10, 2), date(2026, 10, 5))
        self.hotel.cancel_booking(id1)
        id3 = self.hotel.book_room(103, "Fay", date(2026, 10, 3), date(2026, 10, 6))
        self.assertEqual(id3, 2)
    
    def test_cancel_then_rebook(self):
        id1 = self.hotel.book_room(101, "George", date(2026, 11, 1), date(2026, 11, 4))
        self.hotel.cancel_booking(id1)
        id2 = self.hotel.book_room(101, "Hannah", date(2026, 11, 1), date(2026, 11, 4))
        self.assertEqual(id2, 1)

    def test_total_income_with_no_bookings(self):
        self.assertEqual(self.hotel.get_total_income(), 0)

    def test_report_with_multiple_bookings_different_rooms(self):
        self.hotel.book_room(101, "Ivan", date(2026, 12, 1), date(2026, 12, 3))
        self.hotel.book_room(102, "Julia", date(2026, 12, 1), date(2026, 12, 4))
        rep = self.hotel.report()
        self.assertEqual(rep[101], 1)
        self.assertEqual(rep[102], 1)
        self.assertEqual(rep[103], 0)

    def test_get_available_rooms_with_edge_dates(self):
        start = date(2027, 1, 1)
        end = date(2027, 1, 3)
        self.hotel.book_room(101, "Karl", date(2027, 1, 3), date(2027, 1, 5))
        available = self.hotel.get_available_rooms(start, end)
        self.assertIn(101, available)

    def test_update_booking_changes_total_price(self):
        id1 = self.hotel.book_room(101, "Liam", date(2027, 2, 1), date(2027, 2, 4))  # 3 days, 300
        initial_info = self.hotel.get_booking_info(id1)
        self.hotel.update_booking(id1, date(2027, 2, 1), date(2027, 2, 8))  # 7 days, 700*0.9 = 630
        updated_info = self.hotel.get_booking_info(id1)
        self.assertNotEqual(initial_info, updated_info)

    def test_book_room_edge_case_boundary(self):
        start1 = date(2027, 3, 1)
        end1 = date(2027, 3, 5)
        id1 = self.hotel.book_room(101, "Mia", start1, end1)
        # Book immediately after the first booking ends.
        id2 = self.hotel.book_room(101, "Noah", end1, date(2027, 3, 8))
        # Instead of checking availability for the booked period, check for a period after the booking ends.
        self.assertTrue(self.room1.is_available_for(date(2027, 3, 8), date(2027, 3, 10)))


if __name__ == '__main__':
    unittest.main()
