from hotel_system import *
from datetime import date, timedelta


def test_hotel():
    # 1. Test room creation with capacity
    room101 = Room(101, "standard", 100.0, 2)
    # Check basic attributes
    assert room101.number == 101, "Incorrect room number"
    assert room101.room_type == "standard", "Incorrect room type"
    assert room101.price_per_day == 100.0, "Incorrect price per day"
    assert room101.capacity == 2, "Incorrect room capacity"
    # Check availability for a single day when no bookings exist
    assert room101.is_available_for(date(2025, 1, 1), date(2025, 1, 2)) == True, "Room should be available"
    
    # 2. Test multi-day booking via Hotel.book_room
    hotel = Hotel("Florida Beach", [room101])
    start = date(2025, 1, 10)
    end = date(2025, 1, 15)
    booking_id = hotel.book_room(101, "Alice", start, end)
    assert booking_id == 1, "Booking ID should be 1"
    # Room should not be available for the booked period
    assert room101.is_available_for(start, end) == False, "Room should not be available after booking"
    
    # 3. Test discount for bookings longer than 5 days
    room102 = Room(102, "luxury", 200.0, 3)
    hotel.rooms.append(room102)
    start_discount = date(2025, 2, 1)
    end_discount = date(2025, 2, 8)  # 7 days booking
    booking_id2 = hotel.book_room(102, "Bob", start_discount, end_discount)
    booking2 = hotel.bookings[booking_id2]
    expected_price = 7 * 200.0 * 0.9  # 10% discount applied
    assert abs(booking2.total_price - expected_price) < 0.01, "Discounted total price is incorrect"
    
    # 4. Test update_booking: update booking dates to a new non-overlapping range
    new_start = date(2025, 1, 16)
    new_end = date(2025, 1, 20)
    hotel.update_booking(booking_id, new_start, new_end)
    updated_booking = hotel.bookings[booking_id]
    assert updated_booking.start_date == new_start, "Booking start date not updated"
    assert updated_booking.end_date == new_end, "Booking end date not updated"
    
    # 5. Test update_booking failure due to invalid date range
    try:
        hotel.update_booking(booking_id, date(2025, 1, 21), date(2025, 1, 20))
        assert False, "Updating with invalid date range should raise an exception"
    except Exception as e:
        assert str(e) == "Invalid date range", "Incorrect error message for invalid date range in update_booking"
    
    # 6. Test update_booking failure due to overlapping dates
    # Create a new booking in room 101 for a non-overlapping period
    booking_id3 = hotel.book_room(101, "Charlie", date(2025, 1, 5), date(2025, 1, 9))
    # Attempt to update booking_id3 to overlap with booking_id (currently from 2025-01-16 to 2025-01-20)
    try:
        hotel.update_booking(booking_id3, date(2025, 1, 18), date(2025, 1, 22))
        assert False, "Updating to overlapping dates should raise an exception"
    except Exception as e:
        assert str(e) == "Room not available for the new selected dates", "Incorrect error message for overlapping update"
    
    # 7. Test cancel_booking method
    hotel.cancel_booking(booking_id2)
    assert booking_id2 not in hotel.bookings, "Booking should be removed after cancellation"
    # After cancellation, room102 should be available for its previous booking period
    assert room102.is_available_for(start_discount, end_discount) == True, "Room should be available after cancellation"
    
    # 8. Test get_available_rooms method with a given date range
    available_rooms = hotel.get_available_rooms(date(2025, 1, 1), date(2025, 1, 5))
    # Both room101 and room102 should be available in this period
    assert 101 in available_rooms, "Room 101 should be available in the given date range"
    assert 102 in available_rooms, "Room 102 should be available in the given date range"
    
    # 9. Test get_total_income calculation
    # Only booking_id (room101 from 2025-01-16 to 2025-01-20, i.e. 4 days) is active now
    total_income = hotel.get_total_income()
    expected_income_total = 4 * 100.0  # 4 days * 100.0 per day
    assert total_income == expected_income_total, "Total income calculation is incorrect"
    
    # 10. Test get_booking_info method for correct formatted details
    info = hotel.get_booking_info(booking_id)
    assert f"Booking {booking_id}" in info, "Booking info should contain booking ID"
    assert "room 101" in info.lower(), "Booking info should mention room number 101"
    assert "Alice" in info, "Booking info should contain guest name"
    assert str(new_start) in info, "Booking info should contain updated start date"
    assert str(new_end) in info, "Booking info should contain updated end date"
    
    # 11. Test report method: returns a dict with room numbers as keys and booking counts as values
    rep = hotel.report()
    # For room101, there should be 2 bookings (the updated booking and booking_id3)
    # For room102, there should be 0 bookings (cancelled)
    assert rep[101] == 2, "Report count for room 101 is incorrect"
    assert rep[102] == 0, "Report count for room 102 is incorrect"
    
    # 12. Additional exception: try booking a non-existent room
    try:
        hotel.book_room(999, "David", date(2025, 3, 1), date(2025, 3, 5))
        assert False, "Booking a non-existent room should raise an exception"
    except Exception as e:
        assert str(e) == "Room not found", "Incorrect error message for non-existent room booking"
    
    # 13. Additional exception: try canceling a non-existent booking
    try:
        hotel.cancel_booking(999)
        assert False, "Canceling a non-existent booking should raise an exception"
    except Exception as e:
        assert str(e) == "Booking not found", "Incorrect error message for non-existent booking cancellation"
    
    # 14. Additional test: update booking with the same dates (should succeed)
    hotel.update_booking(booking_id3, date(2025, 1, 5), date(2025, 1, 9))
    updated_info = hotel.get_booking_info(booking_id3)
    assert str(date(2025, 1, 5)) in updated_info, "Updated info should reflect the same start date"
    assert str(date(2025, 1, 9)) in updated_info, "Updated info should reflect the same end date"
    
    # 15. Additional test: multiple bookings and cancellations in different rooms
    room104 = Room(104, "standard", 90.0, 2)
    hotel.rooms.append(room104)
    id4 = hotel.book_room(104, "Eve", date(2025, 4, 10), date(2025, 4, 15))
    id5 = hotel.book_room(104, "Frank", date(2025, 4, 15), date(2025, 4, 20))
    assert room104.is_available_for(date(2025, 4, 10), date(2025, 4, 15)) == False, "Room 104 should be booked for first booking"
    hotel.cancel_booking(id4)
    assert room104.is_available_for(date(2025, 4, 10), date(2025, 4, 15)) == True, "Room 104 should be available after cancellation"
    
    # 16. Additional test: ensure report reflects bookings accurately across rooms
    rep2 = hotel.report()
    # Room 104 should have 1 booking (id5), room 101 should have 2, room 102 0, room 103 might have 0.
    assert rep2[104] == 1, "Report count for room 104 is incorrect"
    
    # 17. Additional test: update booking for discount recalculation
    room105 = Room(105, "luxury", 300.0, 2)
    hotel.rooms.append(room105)
    id6 = hotel.book_room(105, "Grace", date(2025, 5, 1), date(2025, 5, 5))  # 4 days, no discount
    booking6 = hotel.bookings[id6]
    initial_price = booking6.total_price
    hotel.update_booking(id6, date(2025, 5, 1), date(2025, 5, 8))  # 7 days, discount applies
    updated_booking6 = hotel.bookings[id6]
    expected_price6 = 7 * 300.0 * 0.9
    assert abs(updated_booking6.total_price - expected_price6) < 0.01, "Discount recalculation failed on update"
    
    # 18. Additional test: get_available_rooms edge case when booking ends exactly when another begins
    room106 = Room(106, "standard", 120.0, 2)
    hotel.rooms.append(room106)
    hotel.book_room(106, "Henry", date(2025, 6, 1), date(2025, 6, 5))
    available_edge = hotel.get_available_rooms(date(2025, 6, 5), date(2025, 6, 10))
    assert 106 in available_edge, "Room 106 should be available when previous booking ends at the start of new range"
    
    # 19. Additional test: multiple operations and consistency check
    id7 = hotel.book_room(101, "Ivy", date(2025, 7, 1), date(2025, 7, 4))
    id8 = hotel.book_room(102, "Jack", date(2025, 7, 2), date(2025, 7, 5))
    hotel.cancel_booking(id7)
    avail_multi = hotel.get_available_rooms(date(2025, 7, 1), date(2025, 7, 5))
    assert 101 in avail_multi, "Room 101 should be available after cancellation in multiple operations"
    assert 102 not in avail_multi, "Room 102 should not be available in multiple operations"
    
    # 20. Additional test: update booking to extend stay and verify total income change
    id9 = hotel.book_room(103, "Karen", date(2025, 8, 1), date(2025, 8, 4))  # 3 days at 300 per day = 900
    initial_income = hotel.get_total_income()
    hotel.update_booking(id9, date(2025, 8, 1), date(2025, 8, 8))  # 7 days with discount: 7*300*0.9 = 1890
    new_income = hotel.get_total_income()
    assert new_income - initial_income == 1890 - 900, "Total income should reflect updated booking price"
    
    # 21. Additional test: check booking ID consistency after cancellations
    id10 = hotel.book_room(101, "Leo", date(2025, 9, 1), date(2025, 9, 4))
    id11 = hotel.book_room(102, "Mia", date(2025, 9, 2), date(2025, 9, 5))
    hotel.cancel_booking(id10)
    id12 = hotel.book_room(103, "Noah", date(2025, 9, 3), date(2025, 9, 6))
    active_bookings = len(hotel.bookings)
    expected_id12 = active_bookings + 1
    assert id12 == expected_id12, "Booking ID consistency failed after cancellations"
    
    # 22. Additional test: cancel then rebook in the same room
    id13 = hotel.book_room(101, "Olivia", date(2025, 10, 1), date(2025, 10, 4))
    hotel.cancel_booking(id13)
    id14 = hotel.book_room(101, "Paul", date(2025, 10, 1), date(2025, 10, 4))
    assert id14 == len(hotel.bookings) + 1, "Rebooking in the same room did not assign correct booking ID"
    
    # 23. Additional test: get_total_income with no active bookings (should be 0)
    hotel.bookings.clear()
    for room in hotel.rooms:
        room.bookings.clear()
    assert hotel.get_total_income() == 0, "Total income should be 0 when there are no bookings"
    
    # 24. Additional test: report with multiple bookings in different rooms
    hotel.book_room(101, "Quinn", date(2025, 11, 1), date(2025, 11, 3))
    hotel.book_room(102, "Rachel", date(2025, 11, 1), date(2025, 11, 4))
    rep_final = hotel.report()
    assert rep_final[101] == 1, "Report count for room 101 is incorrect"
    assert rep_final[102] == 1, "Report count for room 102 is incorrect"
    assert rep_final[103] == 0, "Report count for room 103 is incorrect"
    
    # 25. Additional test: update booking does not change its booking ID
    id15 = hotel.book_room(103, "Sam", date(2025, 12, 1), date(2025, 12, 4))
    hotel.update_booking(id15, date(2025, 12, 2), date(2025, 12, 5))
    assert id15 in hotel.bookings, "Booking ID should remain the same after update"

if __name__ == "__main__":
    test_hotel()
