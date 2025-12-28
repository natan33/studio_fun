from flask import jsonify,g

class ApiResponse:
    @staticmethod
    def success(message="Sucesso",data=None, status_code=200):
        return jsonify({
            "sucess":True,
            "code":"SUCESS",
            "message":message,
            "trace_id":g.get("trace_id"),
            "data":data,
            "errors":None,
        }), status_code