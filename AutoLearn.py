import random
import requests
import json
from typing import Dict, Any
import time


class MingShiClass:
    """名师课堂API客户端"""

    def __init__(self):
        self.base_url = "https://api.mingshiclass.com"
        self.session = requests.Session()
        self.token = None
        self.uid = None
        self.teacher_id = None

        # 基础headers
        self.headers = {
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Connection": "keep-alive",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "Origin": "https://saas.mingshiclass.com",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Mobile Safari/537.36",
            "sec-ch-ua": '"Not A(Brand";v="8", "Chromium";v="132", "Google Chrome";v="132"',
            "sec-ch-ua-mobile": "?1",
            "sec-ch-ua-platform": '"Android"',
        }

        # 固定参数
        self.file_size_at_path = "a9b7ba70783b617e9998dc4dd82eb3c5"
        self.client_source = "web"
        self.client_version = "1.0"
        self.enter_type = "integral"

        # 学习进度存储
        self.learning_progress = {}
        self.completed_courses = set()
        self.current_course_id = None

    def login(self, mobile: str, password: str) -> Dict[str, Any]:
        """
        用户登录

        Args:
            mobile: 手机号
            password: 密码

        Returns:
            dict: 登录结果
        """
        url = f"{self.base_url}/user/authLogin1.0"

        # 构建登录参数
        data = {
            "mobile": mobile,
            "password": password,
            "fileSizeAtPath": self.file_size_at_path,
            "clientSource": self.client_source,
            "clientVersion": self.client_version,
            "token": "",
            "uid": "",
            "teacherId": "",
            "enterType": self.enter_type,
        }

        print("=" * 60)
        print("【登录】正在登录...")
        print(f"手机号: {mobile}")
        print(f"请求URL: {url}")

        try:
            response = self.session.post(
                url, json=data, headers=self.headers, timeout=30
            )

            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()

                # 检查登录是否成功
                if result.get("header", {}).get("code") == "200":
                    # 提取token和用户信息
                    data_info = result.get("data", {})
                    self.token = data_info.get("token", "")
                    self.uid = data_info.get("uid", "")
                    self.teacher_id = data_info.get("uid", "")  # teacherId和uid一样

                    print(f"[成功] 登录成功!")
                    print(f"Token: {self.token}")
                    print(f"UID: {self.uid}")
                    print(f"TeacherId: {self.teacher_id}")

                    return {
                        "success": True,
                        "data": result,
                        "token": self.token,
                        "uid": self.uid,
                        "teacher_id": self.teacher_id,
                    }
                else:
                    print(
                        f"[失败] {result.get('header', {}).get('codeMsg', '未知错误')}"
                    )
                    return {
                        "success": False,
                        "data": result,
                        "message": result.get("header", {}).get("codeMsg", "登录失败"),
                    }
            else:
                print(f"[失败] HTTP状态码: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "data": response.text,
                }

        except requests.exceptions.RequestException as e:
            print(f"[错误] 请求失败: {e}")
            return {"success": False, "error": str(e)}

    def get_course_list(
        self,
        pageindex: int = 1,
        count_of_page: int = 20,
        keyword: str = "",
        theme_id: str = "",
        setmeal_id: str = "",
    ) -> Dict[str, Any]:
        """
        获取课程列表
        Args:
            pageindex: 页码，默认1
            count_of_page: 每页数量，默认20
            keyword: 搜索关键词
            theme_id: 主题ID
            setmeal_id: 套餐ID
        Returns:
            dict: 课程列表数据
        """
        # 检查是否已登录
        if not self.token:
            print("[错误] 请先登录！")
            return {"success": False, "message": "请先登录"}

        url = f"{self.base_url}/shixun/getFreedomStudyCoursePackList1.0"

        # 构建请求参数
        data = {
            "setmealId": setmeal_id,
            "totalCount": 0,
            "pageindex": pageindex,
            "themeId": theme_id,
            "pageCount": 0,
            "keyword": keyword,
            "countOfPage": count_of_page,
            "fileSizeAtPath": self.file_size_at_path,
            "clientSource": self.client_source,
            "clientVersion": self.client_version,
            "token": self.token,
            "uid": self.uid,
            "teacherId": self.teacher_id,
            "enterType": self.enter_type,
        }

        print("\n" + "=" * 60)
        print("【获取课程列表】")
        print("=" * 60)
        print(f"页码: {pageindex}")
        print(f"每页数量: {count_of_page}")
        print(f"请求URL: {url}")

        try:
            response = self.session.post(
                url, json=data, headers=self.headers, timeout=30
            )
            print(f"状态码: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                # 检查响应码
                if result.get("header", {}).get("code") == "200":
                    course_data = result.get("data", {})
                    course_list = course_data.get("shixunCoursepackList", [])
                    total_count = course_data.get("totalCount", 0)
                    page_count = course_data.get("pageCount", 0)

                    print(f"[成功] 获取课程列表成功!")
                    print(f"总课程数: {total_count}")
                    print(f"总页数: {page_count}")
                    print(f"当前页课程数: {len(course_list)}")

                    # 显示课程概要
                    if course_list:
                        print("\n课程列表:")
                        print("-" * 60)
                        for idx, course in enumerate(course_list, 1):
                            print(f"{idx}. {course.get('coursepackName', '未知')}")
                            print(f"   ID: {course.get('coursepackId', '')}")
                            print(f"   课程数: {course.get('courseCount', 0)}")
                            print(f"   已学课时: {course.get('studyCount', '')}")
                            print(f"   简介: {course.get('introduceInfo', '')[:50]}...")
                            print("-" * 60)

                    return {
                        "success": True,
                        "data": result,
                        "course_list": course_list,
                        "total_count": total_count,
                        "page_count": page_count,
                        "current_page": pageindex,
                    }
                else:
                    print(
                        f"[失败] {result.get('header', {}).get('codeMsg', '未知错误')}"
                    )
                    return {
                        "success": False,
                        "data": result,
                        "message": result.get("header", {}).get(
                            "codeMsg", "获取课程失败"
                        ),
                    }
            else:
                print(f"[失败] HTTP状态码: {response.status_code}")
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "data": response.text,
                }

        except requests.exceptions.RequestException as e:
            print(f"[错误] 请求失败: {e}")
            return {"success": False, "error": str(e)}

    def get_course_details(self, coursepack_id: str) -> Dict[str, Any]:
        """
        获取课程包详情
        Args:
            coursepack_id: 课程包ID
        Returns:
            dict: 课程详情
        """
        url = f"{self.base_url}/shixun/getFreedomStudyCourseList1.0"

        data = {
            "sort": "",
            "courseTypeId": "",
            "coursepackId": coursepack_id,
            "packtagCode": "",
            "shapeCode": "",
            "categoryId": "",
            "studentsegCode": "",
            "hasPlan": 1,
            "pageindex": 1,
            "pageCount": 0,
            "countOfPage": 999,
            "totalCount": 0,
            "courseName": "",
            "fileSizeAtPath": self.file_size_at_path,
            "clientSource": self.client_source,
            "clientVersion": self.client_version,
            "token": self.token,
            "uid": self.uid,
            "teacherId": self.teacher_id,
            "enterType": self.enter_type,
        }

        try:
            response = self.session.post(
                url, json=data, headers=self.headers, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("header", {}).get("code") == "200":
                    courses = result.get("data", {}).get("shixunCourseList", [])
                    print(f"  获取到 {len(courses)} 个视频")
                    return courses
                else:
                    print(
                        f"  [失败] {result.get('header', {}).get('codeMsg', '获取失败')}"
                    )
                    return []
            else:
                print(f"  [失败] HTTP状态码: {response.status_code}")
                return []

        except Exception as e:
            print(f"  [错误] 获取课程列表失败: {e}")
            return []

    def submit_study_record(
        self, course_id: str, start_time: int, time_point: int, duration: int
    ) -> bool:
        """提交学习记录"""
        url = f"{self.base_url}/shixun/submitStudyRecord1.0"

        data = {
            "clientSource": self.client_source,
            "clockVideoId": "",
            "startTime": start_time,
            "timePoint": time_point,
            "duration": duration,
            "learnSource": 1,
            "learnType": "1",
            "courseId": course_id,
            "fileSizeAtPath": self.file_size_at_path,
            "clientVersion": self.client_version,
            "token": self.token,
            "uid": self.uid,
            "teacherId": self.teacher_id,
            "enterType": self.enter_type,
        }

        try:
            response = self.session.post(
                url, json=data, headers=self.headers, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                if result.get("header", {}).get("code") == "200":
                    # 使用divmod函数进行转换
                    minutes, sec = divmod(time_point, 60)
                    print(
                        f"  提交学习记录成功: 本次从{minutes}分{sec}秒位置开始学习，学习了{duration}秒。"
                    )
                    return True
                else:
                    return False
            else:
                return False

        except Exception as e:
            print(f"  [错误] 提交学习记录失败: {e}")
            return False

    def learn_course(self, course: Dict[str, Any]) -> bool:
        """学习单个课程视频"""
        course_id = course.get("courseId")
        course_name = course.get("courseName", "未知课程")
        duration = course.get("duration", 0)
        learn_status = course.get("learnStatus", 0)
        last_learn_time = course.get("lastLearnTime", 0)

        print(f"\n  开始学习: {course_name}")
        print(f"  视频时长: {duration}秒")

        # 检查是否已学完
        if learn_status == 2:  # 2表示已学完
            print(f"  ✓ 已学完，跳过")
            return True

        # 检查是否已完成（自定义）
        if course_id in self.completed_courses:
            print(f"  ✓ 已完成，跳过")
            return True

        # 从上次学习位置继续
        start_time = int(time.time() * 1000)
        current_time = last_learn_time

        print(f"  上次学习位置: {current_time}秒")
        print(f"  开始学习...")

        # 模拟学习过程（每次提交3-5秒的进度）
        total_learned = current_time

        # 分多次提交学习记录，模拟真实学习
        while total_learned < duration:
            # 每次学习3-8秒
            learn_duration = random.randint(100, 600)
            total_learned += learn_duration

            if total_learned > duration:
                total_learned = duration

            # 提交学习记录
            time_point = total_learned
            success = self.submit_study_record(
                course_id=course_id,
                start_time=start_time,
                time_point=time_point,
                duration=learn_duration,
            )

            if success:
                progress = (total_learned / duration) * 100
                print(f"    进度: {progress:.1f}% ({total_learned}/{duration}秒)")

                # 检查是否学完
                if total_learned >= duration:
                    print(f"  ✓ 学习完成!")
                    self.completed_courses.add(course_id)
                    return True
            else:
                print(f"  [警告] 提交学习记录失败")

            # 随机等待，模拟真实学习
            time.sleep(random.uniform(2, 4))

        # 检查是否学完
        if total_learned >= duration:
            print(f"  ✓ 学习完成!")
            self.completed_courses.add(course_id)
            return True

        print(f"  ⚠ 学习中断，进度: {(total_learned/duration)*100:.1f}%")
        return False


def main():
    """主函数 - 完整流程演示"""
    # 创建客户端
    client = MingShiClass()
    # 1. 登录
    print("\n" + "=" * 60)
    print("名师课堂 API 测试")
    print("=" * 60)

    mobile = "130xxxxxxx"
    password = "wuyanan123"

    login_result = client.login(mobile, password)

    if not login_result.get("success"):
        print("\n[终止] 登录失败，程序退出")
        return

    print("\n" + "=" * 60)
    print("登录成功！继续获取课程列表...")
    print("=" * 60)

    # 2. 获取课程列表（第一页）
    course_result = client.get_course_list(pageindex=1, count_of_page=20)

    if course_result.get("success"):
        print("\n" + "=" * 60)
        print("【课程列表获取完成】")
        # 保存课程列表到文件
        with open("course_list.json", "w", encoding="utf-8") as f:
            json.dump(course_result.get("data", {}), f, ensure_ascii=False, indent=2)
        print("\n课程数据已保存到 course_list.json")

    # 4. 显示所有课程ID（便于后续操作）
    if course_result.get("success"):
        courses = course_result.get("course_list", [])
        print("\n" + "=" * 60)
        print("【所有课程ID列表】")
        print("=" * 60)
        for course in courses:
            print(f"{course.get('coursepackName')}: {course.get('coursepackId')}")
            # 获取当前大课（coursepack）下的所有小课视频（courseId），并逐个播放
            shixunCourseList = client.get_course_details(course.get("coursepackId"))
            for shixunCourse in shixunCourseList:
                client.learn_course(course=shixunCourse)


if __name__ == "__main__":
    main()
