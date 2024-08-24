directors = [
    "Alisher Xudoyberdiyev",
    "Dilshod Qodirov",
    "Otabek Karimov",
    "Shavkat Ismoilov"
]

phones = [
    "+998901234567",
    "+998901234568",
    "+998901234569",
    "+998901234570"
]

teachers = [25, 30, 28, 27]
students = [500, 450, 470, 480]

schools_count = 8

def generate_schools(district_id):
    if district_id % 2 == 1:
        director_list = [directors[0], directors[1]]
        phone_list = [phones[0], phones[1]]
        teacher_list = [teachers[0], teachers[1]]
        student_list = [students[0], students[1]]
    else:
        director_list = [directors[2], directors[3]]
        phone_list = [phones[2], phones[3]]
        teacher_list = [teachers[2], teachers[3]]
        student_list = [students[2], students[3]]

    return [
        {
            "name": f"{i + 1}-maktab",
            "director": director_list[i % len(director_list)],
            "phone": phone_list[i % len(phone_list)],
            "teachers": teacher_list[i % len(teacher_list)],
            "students": student_list[i % len(student_list)]
        }
        for i in range(schools_count)
    ]

schools = {i: generate_schools(i) for i in range(1, 15)}
