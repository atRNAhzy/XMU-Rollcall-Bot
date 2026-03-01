import time
from .verify import send_code, send_radar
from .wx_send import wx_send


def notify_rollcall(content, title="签到结果通知"):
    try:
        wx_send(content, title=title)
    except Exception as exc:
        print(f"通知发送失败：{exc}")

def process_rollcalls(data, session):
    """处理签到数据"""
    data_empty = {'rollcalls': []}
    result = handle_rollcalls(data, session)
    if False in result:
        return data_empty
    else:
        return data

def extract_rollcalls(data):
    """提取签到信息"""
    rollcalls = data['rollcalls']
    result = []
    if rollcalls:
        rollcall_count = len(rollcalls)
        for rollcall in rollcalls:
            result.append({
                'course_title': rollcall['course_title'],
                'created_by_name': rollcall['created_by_name'],
                'department_name': rollcall['department_name'],
                'is_expired': rollcall['is_expired'],
                'is_number': rollcall['is_number'],
                'is_radar': rollcall['is_radar'],
                'rollcall_id': rollcall['rollcall_id'],
                'rollcall_status': rollcall['rollcall_status'],
                'scored': rollcall['scored'],
                'status': rollcall['status']
            })
    else:
        rollcall_count = 0
    return rollcall_count, result

def handle_rollcalls(data, session):
    """处理签到流程"""
    count, rollcalls = extract_rollcalls(data)
    answer_status = [False for _ in range(count)]

    if count:
        print(time.strftime("%H:%M:%S", time.localtime()), f"New rollcall(s) found!\n")
        for i in range(count):
            print(f"{i+1} of {count}:")
            print(f"Course name: {rollcalls[i]['course_title']}, rollcall created by {rollcalls[i]['department_name']} {rollcalls[i]['created_by_name']}.")

            if rollcalls[i]['is_radar']:
                temp_str = "Radar rollcall"
            elif rollcalls[i]['is_number']:
                temp_str = "Number rollcall"
            else:
                temp_str = "QRcode rollcall"
            print(f"Rollcall type: {temp_str}\n")
            rollcall_desc = f"课程《{rollcalls[i]['course_title']}》{temp_str}"

            if (rollcalls[i]['status'] == 'absent') & (rollcalls[i]['is_number']) & (not rollcalls[i]['is_radar']):
                if send_code(session, rollcalls[i]['rollcall_id']):
                    # TODO: Handle rollcall success event (number code flow).
                    answer_status[i] = True
                    notify_rollcall(f"{rollcall_desc} 签到成功。")
                else:
                    # TODO: Handle rollcall failure event (number code flow).
                    print("Answering failed.")
                    notify_rollcall(f"{rollcall_desc} 签到失败，请尽快处理。")
            elif rollcalls[i]['status'] == 'on_call_fine':
                # TODO: Handle rollcall success event (already answered state).
                print("Already answered.")
                answer_status[i] = True
                notify_rollcall(f"{rollcall_desc} 已完成签到，无需重复操作。")
            elif rollcalls[i]['is_radar']:
                if send_radar(session, rollcalls[i]['rollcall_id']):
                    # TODO: Handle rollcall success event (radar flow).
                    answer_status[i] = True
                    notify_rollcall(f"{rollcall_desc} 签到成功。")
                else:
                    # TODO: Handle rollcall failure event (radar flow).
                    print("Answering failed.")
                    notify_rollcall(f"{rollcall_desc} 签到失败，请尽快处理。")
            else:
                # TODO: qrcode rollcall
                print("Answering failed. QRcode rollcall not supported yet.")
                notify_rollcall(f"{rollcall_desc} 签到失败，暂不支持二维码签到。")

    return answer_status

